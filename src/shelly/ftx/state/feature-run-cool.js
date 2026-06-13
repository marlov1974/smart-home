// state feature-run-cool 1.2.0
var COOL_RUN_PCT_MIN = 0;
var COOL_RUN_DT_MIN_C = 0.5;

function applyCoolRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var cool = telAct.cool || {};
  var t = telM.t || {};

  ctx.run.cool = b(
    on(cool) &&
    pct(cool) > COOL_RUN_PCT_MIN &&
    (sget(t, "post_vvx", 0) - sget(t, "to_house", 0)) >= COOL_RUN_DT_MIN_C
  );

  cb();
}
