// brain io-forced-mode 2.1.0
var KEY_MODE_FORCED_STATE = "ftx.mode_forced_state";

function readForcedMode(ctx, cb) {
  ctx.forced.mode = MODE_STD;
  ctx.forced.cycles = 0;

  kvsGet(KEY_MODE_FORCED_STATE, function (v) {
    if (v && typeof v === "object") {
      ctx.forced.mode = (v.mode === MODE_BST || v.mode === MODE_FIRE || v.mode === MODE_STD) ? v.mode : MODE_STD;
      ctx.forced.cycles = i(n(v.cycles, 0));
    }
    cb();
  });
}

function writeForcedMode(ctx, cb) {
  kvsSet(KEY_MODE_FORCED_STATE, { mode: ctx.forced.mode, cycles: ctx.forced.cycles }, cb);
}
