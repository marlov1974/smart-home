// brain feature-thermal 2.7.0-signed-energy-demand
var ENERGY_DEADBAND_KWH_DAY = 0.3;
var HOUSE_RECOVERY_KWH_PER_C = 100.0;
var HOUSE_LOSS_KWH_DAY_PER_C = 12.5;
var BASE_INTERNAL_KWH_DAY = 42.0;
var COOL_MAX_SUPPLY_PCT = 75;
var HEAT_MAX_SUPPLY_PCT = 75;
var THERMAL_MIN_SUPPLY_PCT = 20;
var HEAT_STEP_PCT = 8;
var COOL_STEP_PCT = 5;
var THERMAL_HOLD_BAND_C = 0.2;

function r5(v) { return 5 * i(n(v, 0) / 5); }

function calcEnergyNeedKwhDay(ctx, houseC, avgOutC, solarKwh) {
  var recovery = (ctx.sig.house_target_c - houseC) * HOUSE_RECOVERY_KWH_PER_C;
  var balance = HOUSE_LOSS_KWH_DAY_PER_C * (houseC - avgOutC) - BASE_INTERNAL_KWH_DAY - solarKwh;
  return recovery + balance;
}

function supplyPctForEnergy(kwhDayAbs, deltaC, maxPct) {
  var d = n(deltaC, 0);
  var p;
  if (kwhDayAbs <= 0) return 0;
  if (d < 0.5) d = 0.5;
  p = r5(kwhDayAbs / (0.077 * d));
  return clipPct(clip(p, THERMAL_MIN_SUPPLY_PCT, maxPct));
}

function rawHeatTargetFromEnergy(houseC, kwhDay, supPct) {
  if (kwhDay <= 0 || supPct <= 0) return houseC;
  return houseC + kwhDay / airKwhDayPerC(supPct);
}

function rawCoolTargetFromEnergy(houseC, kwhDayAbs, supPct) {
  if (kwhDayAbs <= 0 || supPct <= 0) return houseC;
  return houseC - kwhDayAbs / airKwhDayPerC(supPct);
}

function calcThermal(ctx) {
  var h = n(ctx.inp.t_house_c, ctx.sig.house_target_c);
  var avgOut = n(ctx.weather.temp_avg_today_c, n(ctx.weather.temp_now_c, ctx.inp.t_out_c));
  var s = n(ctx.weather.solar_kwh_today, 0);
  var energy = calcEnergyNeedKwhDay(ctx, h, avgOut, s);
  var eabs = energy < 0 ? -energy : energy;
  var maxHeatTarget = TARGET_TO_HOUSE_MAX_C;
  var minCoolTarget = ctx.sig.min_supply_temp_c;
  var baseSup = clipPct(ctx.sig.std_sup_pct || THERMAL_MIN_SUPPLY_PCT);
  var requiredSup = 0;
  var target = ctx.sig.target_to_house_c;
  var rawTarget = target;
  var e = 0;

  ctx.sig.energy_need_kwh_day = d1(energy);
  ctx.sig.cool_need_kwh_day = energy < 0 ? d1(eabs) : 0;
  ctx.sig.heat_need_kwh_day = energy > 0 ? d1(eabs) : 0;
  ctx.sig.cool_candidate_pct = 0;
  ctx.sig.heat_candidate_pct = 0;
  ctx.sig.thermal_sup_pct = 0;
  ctx.sig.thermal_mode = "NEU";

  if (energy < -ENERGY_DEADBAND_KWH_DAY) {
    ctx.sig.thermal_mode = "COOL";
    rawTarget = rawCoolTargetFromEnergy(h, eabs, baseSup);
    if (rawTarget < minCoolTarget) {
      requiredSup = supplyPctForEnergy(eabs, h - minCoolTarget, COOL_MAX_SUPPLY_PCT);
      ctx.sig.thermal_sup_pct = max2(0, requiredSup - baseSup);
      target = minCoolTarget;
    } else {
      target = rawTarget;
    }
  } else if (energy > ENERGY_DEADBAND_KWH_DAY) {
    ctx.sig.thermal_mode = "HEAT";
    rawTarget = rawHeatTargetFromEnergy(h, eabs, baseSup);
    if (rawTarget > maxHeatTarget) {
      requiredSup = supplyPctForEnergy(eabs, maxHeatTarget - h, HEAT_MAX_SUPPLY_PCT);
      ctx.sig.thermal_sup_pct = max2(0, requiredSup - baseSup);
      target = maxHeatTarget;
    } else {
      target = rawTarget;
    }
  }

  ctx.sig.target_to_house_c = d1(clip(target, minCoolTarget, maxHeatTarget));

  if (ctx.sig.thermal_mode === "COOL") {
    e = ctx.inp.t_to_house_c - ctx.sig.target_to_house_c;
    if (ctx.sig.full_air_ready && e > THERMAL_HOLD_BAND_C) ctx.sig.cool_candidate_pct = clipPct(ctx.inp.cool_pct_actual + COOL_STEP_PCT);
    else if (ctx.sig.full_air_ready && e < -THERMAL_HOLD_BAND_C) ctx.sig.cool_candidate_pct = clipPct(ctx.inp.cool_pct_actual - COOL_STEP_PCT);
    else ctx.sig.cool_candidate_pct = ctx.sig.full_air_ready ? clipPct(ctx.inp.cool_pct_actual) : 0;
  }

  if (ctx.sig.thermal_mode === "HEAT") {
    e = ctx.sig.target_to_house_c - ctx.inp.t_to_house_c;
    if (ctx.sig.full_air_ready && e > THERMAL_HOLD_BAND_C) ctx.sig.heat_candidate_pct = clipPct(ctx.inp.heat_pct_actual + HEAT_STEP_PCT);
    else if (ctx.sig.full_air_ready && e < -THERMAL_HOLD_BAND_C) ctx.sig.heat_candidate_pct = clipPct(ctx.inp.heat_pct_actual - HEAT_STEP_PCT);
    else ctx.sig.heat_candidate_pct = ctx.sig.full_air_ready ? clipPct(ctx.inp.heat_pct_actual) : 0;
  }

  ctx.sig.supply_delta_post_c = ctx.sig.target_to_house_c - ctx.inp.t_post_vvx_c;
  ctx.sig.delta_to_house_c = ctx.sig.target_to_house_c - ctx.inp.t_to_house_c;
}
