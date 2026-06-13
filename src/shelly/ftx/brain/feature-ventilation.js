// brain feature-ventilation 2.5.0-supply-primary
var SUP_MIN_PCT = 15;
var SUP_MAX_PCT = 90;
var CO2_PPM_AT_25 = 500;
var CO2_PPM_AT_75 = 750;
var CO2_SUP_PCT_AT_25 = 25;
var CO2_SUP_PCT_AT_75 = 75;
var TEMP_ERR_MAX_C = 3.0;
var TEMP_SUP_BASE_PCT = 15;
var TEMP_SUP_SLOPE_PCT_PER_C = 20;

function calcStdSupplyPctFromPpm(ppm) {
  var pct;
  pct = CO2_SUP_PCT_AT_25 + (n(ppm, CO2_PPM_AT_25) - CO2_PPM_AT_25) * ((CO2_SUP_PCT_AT_75 - CO2_SUP_PCT_AT_25) / (CO2_PPM_AT_75 - CO2_PPM_AT_25));
  return clipPct(clip(pct, SUP_MIN_PCT, SUP_MAX_PCT));
}

function calcStdSupplyPctFromTemp(houseC, setC) {
  var err = clip(abs(n(houseC, setC) - n(setC, houseC)), 0, TEMP_ERR_MAX_C);
  var pct = TEMP_SUP_BASE_PCT + err * TEMP_SUP_SLOPE_PCT_PER_C;
  return clipPct(clip(pct, SUP_MIN_PCT, SUP_MAX_PCT));
}

function extractPctFromSupplyPct(supPct) {
  return clipPct(Math.round((n(supPct, 0) + 1) / 0.9));
}

function supplyPctFromExtractPct(extPct) {
  return clipPct(Math.round(0.9 * n(extPct, 0) - 1));
}

function airKwhDayPerC(supPct) {
  return 0.077 * clip(n(supPct, 0), 15, 90);
}

function calcVentilation(ctx) {
  ctx.sig.full_air_ready = b(ctx.inp.dmp_run && ctx.inp.sup_run && ctx.inp.ext_run);
  ctx.sig.co2_sup_pct = calcStdSupplyPctFromPpm(ctx.inp.ppm_house);
  ctx.sig.temp_sup_pct = calcStdSupplyPctFromTemp(ctx.inp.t_house_c, ctx.sig.house_target_c);
  ctx.sig.std_sup_pct = max2(ctx.sig.co2_sup_pct, ctx.sig.temp_sup_pct);
  ctx.sig.std_ext_pct = extractPctFromSupplyPct(ctx.sig.std_sup_pct);
}
