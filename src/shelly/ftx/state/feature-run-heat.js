// state feature-run-heat 1.2.0
var HEAT_RUN_PCT_MIN = 0;
var HEAT_RUN_DT_MIN_C = 0.5;

function applyHeatRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var heat = telAct.heat || {};
  var t = telM.t || {};

  ctx.run.heat = b(
    on(heat) &&
    pct(heat) > HEAT_RUN_PCT_MIN &&
    (sget(t, "to_house", 0) - sget(t, "post_vvx", 0)) >= HEAT_RUN_DT_MIN_C
  );

  cb();
}
