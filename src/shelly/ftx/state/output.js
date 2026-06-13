// state output 1.8.0-device-telemetry
function writeTelemetryCompat(ctx, cb) {
  kvsSet(KEY_TEL_M, ctx.telM || {}, function () {
    kvsSet(KEY_TEL_X, ctx.telX || {}, function () {
      kvsSet(KEY_TEL_ACT, ctx.telAct || {}, cb);
    });
  });
}

function writeStateOutput(ctx, cb) {
  kvsSet(KEY_STATE_RUN, ctx.run || {}, cb);
}

function writeStateStatus(ctx, cb) {
  var run = ctx.run || {};
  log("OK SR=" + run.sup + " ER=" + run.ext + " VR=" + run.vvx + " H=" + run.heat + " C=" + run.cool);
  if (cb) cb();
}
