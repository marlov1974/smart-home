// brain feature-failsafe 2.7.2-supply-primary-failsafe
var FREEZE_POST_VVX_MIN_C = 0.0;
var FAILSAFE_WRONG_DIR_DB_C = 1.0;
var FAILSAFE_COLD_SUP_PCT = 15;
var FAILSAFE_MILD_SUP_PCT = 25;
var FAILSAFE_HEAT_PCT_MIN = 100;

function calcFailsafe(ctx) {
  var heatWrongDir = b(
    ctx.inp.t_house_c < ctx.sig.house_target_c &&
    ctx.inp.t_to_house_c < (ctx.inp.t_house_c - FAILSAFE_WRONG_DIR_DB_C) &&
    ctx.inp.heat_pct_actual >= FAILSAFE_HEAT_PCT_MIN
  );
  var coolWrongDir = b(
    ctx.inp.t_house_c > ctx.sig.house_target_c &&
    ctx.inp.t_to_house_c > (ctx.inp.t_house_c + FAILSAFE_WRONG_DIR_DB_C)
  );

  ctx.sig.freeze_guard_active = b(ctx.inp.t_post_vvx_c < FREEZE_POST_VVX_MIN_C);
  ctx.sig.failsafe_active = b(heatWrongDir || coolWrongDir);
  ctx.sig.failsafe_sup_pct = (ctx.inp.t_out_c < 0) ? FAILSAFE_COLD_SUP_PCT : FAILSAFE_MILD_SUP_PCT;
}
