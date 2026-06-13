// brain feature-forced-mode 2.1.0
var FORCED_MODE_MAX_CYCLES = 240;
var CMD_MODE_ID = 200;

function applyForcedModeTimeout(ctx, cb) {
  if (!isForcedMode(ctx.cmd.mode)) {
    ctx.forced.mode = MODE_STD;
    ctx.forced.cycles = 0;
    writeForcedMode(ctx, cb);
    return;
  }

  if (ctx.forced.mode === ctx.cmd.mode) ctx.forced.cycles = ctx.forced.cycles + 1;
  else {
    ctx.forced.mode = ctx.cmd.mode;
    ctx.forced.cycles = 1;
  }

  if (ctx.forced.cycles >= FORCED_MODE_MAX_CYCLES) {
    ctx.forced.mode = MODE_STD;
    ctx.forced.cycles = 0;
    ctx.cmd.mode = MODE_STD;
    enumSet(CMD_MODE_ID, MODE_STD, function () { writeForcedMode(ctx, cb); });
    return;
  }

  writeForcedMode(ctx, cb);
}
