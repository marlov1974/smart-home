// state feature-run-dampers 1.2.0
function applyDampersRun(ctx, cb) {
  var telAct = ctx.telAct || {};
  var dmp = telAct.dmp || {};

  ctx.run.dmp = b(on(dmp));

  cb();
}
