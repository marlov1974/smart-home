// state perf-power 1.6.3-base-power-only
var BASE_POWER_ID = 201;
var BASE_POWER_W = 14;

function calcPower(telM, telAct) {
  return BASE_POWER_W;
}

function calcPowerFeature(ctx) {
  ctx.power_w = BASE_POWER_W;
}

function writePowerFeature(ctx, cb) {
  numberSet(BASE_POWER_ID, BASE_POWER_W, cb);
}
