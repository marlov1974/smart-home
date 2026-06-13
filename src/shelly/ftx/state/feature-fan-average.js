// state feature-fan-average 1.2.0
var FAN_SPEED_AVG_ID = 203;

function calcFanAverage(telM, telAct) {
  var sup = telAct && telAct.sup ? telAct.sup : {};
  var ext = telAct && telAct.ext ? telAct.ext : {};
  return clipPct((pct(sup) + pct(ext)) / 2);
}

function applyFanAverageFeature(ctx, cb) {
  var fanAvg = calcFanAverage(ctx.telM || {}, ctx.telAct || {});
  numberSet(FAN_SPEED_AVG_ID, fanAvg, cb);
}
