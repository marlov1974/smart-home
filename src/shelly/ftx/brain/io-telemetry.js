// brain io-telemetry 2.0.0
function readTelemetry(ctx, cb) {
  kvsGet(KEY_TEL_M, function (m) {
    ctx.telM = (m && typeof m === "object") ? m : {};
    kvsGet(KEY_TEL_ACT, function (a) {
      ctx.telAct = (a && typeof a === "object") ? a : {};
      cb();
    });
  });
}
