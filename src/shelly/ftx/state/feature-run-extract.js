// state feature-run-extract 1.2.0
var EXTRACT_RUN_PCT_MIN = 10;
var EXTRACT_RUN_RPM_MIN = 250;
var EXTRACT_RUN_PA_MIN = 5;

function applyExtractRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var ext = telAct.ext || {};
  var rpm = telM.rpm || {};
  var pa = telM.pa || {};

  ctx.run.ext = b(
    on(ext) &&
    pct(ext) > EXTRACT_RUN_PCT_MIN &&
    sget(rpm, "ext", 0) > EXTRACT_RUN_RPM_MIN &&
    sget(pa, "ext", 0) >= EXTRACT_RUN_PA_MIN
  );

  cb();
}
