// state feature-run-vvx 1.2.0
var VVX_RUN_RPM_MIN = 4;

function applyVvxRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var vvx = telAct.vvx || {};
  var rpm = telM.rpm || {};

  ctx.run.vvx = b(on(vvx) && sget(rpm, "vvx", 0) > VVX_RUN_RPM_MIN);

  cb();
}
