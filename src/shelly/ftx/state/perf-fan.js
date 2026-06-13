// state perf-fan 1.3.0-classic-calc-rpc-write
var FAN_SPEED_AVG_ID = 203;

function calcFanAverage(telM, telAct) {
  var sup = telAct && telAct.sup ? telAct.sup : {};
  var ext = telAct && telAct.ext ? telAct.ext : {};
  return clipPct((pct(sup) + pct(ext)) / 2);
}

function calcFanAverageFeature(ctx) {
  ctx.fan_avg_pct = calcFanAverage(ctx.telM || {}, ctx.telAct || {});
}

function writeFanAverageFeature(ctx, cb) {
  numberSet(FAN_SPEED_AVG_ID, ctx.fan_avg_pct || 0, cb);
}
