// brain feature-target 2.7.0-comfort-target-only
var DP_A = 17.62;
var DP_B = 243.12;

var TARGET_TO_HOUSE_MIN_C = 12.0;
var TARGET_TO_HOUSE_MAX_C = 30.0;

function calcDewPointC(tempC, rhPct) {
  var rh = clip(rhPct, 1, 100);
  var gamma = (DP_A * tempC) / (DP_B + tempC) + Math.log(rh / 100);
  return (DP_B * gamma) / (DP_A - gamma);
}

function calcTarget(ctx) {
  var targetC = n(ctx.cmd.house_temp_c, 20.0);
  var dewPointHouseC;

  ctx.sig.night_setback_active = 0;
  ctx.sig.weather_bias_c = 0;

  dewPointHouseC = calcDewPointC(ctx.inp.t_house_c, ctx.inp.rh_house_pct);
  ctx.sig.house_target_c = d1(targetC);
  ctx.sig.dewpoint_house_c = d1(dewPointHouseC);
  ctx.sig.min_supply_temp_c = d1(max2(dewPointHouseC, TARGET_TO_HOUSE_MIN_C));
  ctx.sig.target_to_house_c = clip(targetC, TARGET_TO_HOUSE_MIN_C, TARGET_TO_HOUSE_MAX_C);
  ctx.sig.supply_delta_post_c = ctx.sig.target_to_house_c - ctx.inp.t_post_vvx_c;
  ctx.sig.delta_to_house_c = ctx.sig.target_to_house_c - ctx.inp.t_to_house_c;
}
