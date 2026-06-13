// state perf 1.2.1
var TOTAL_POWER_ID = 201;
var IDLE_POWER_W = 14;
var DAMPERS_POWER_W = 8;

var VVX_EFFICIENCY_ID = 202;
var KEY_STATE_HIST = "ftx.state.hist";
var VVX_EFF_DEN_MIN_C = 3.0;

var FAN_SPEED_AVG_ID = 203;

function calcPower(telM, telAct) {
  var sup = telAct && telAct.sup ? telAct.sup : {};
  var ext = telAct && telAct.ext ? telAct.ext : {};
  var vvx = telAct && telAct.vvx ? telAct.vvx : {};
  var heat = telAct && telAct.heat ? telAct.heat : {};
  var cool = telAct && telAct.cool ? telAct.cool : {};
  var dmp = telAct && telAct.dmp ? telAct.dmp : {};
  var total = IDLE_POWER_W + (on(dmp) ? DAMPERS_POWER_W : 0) + w(sup) + w(ext) + w(vvx) + w(heat) + w(cool);
  return i(clip(total, 0, 9999));
}

function applyPowerFeature(ctx, cb) {
  var totalW = calcPower(ctx.telM || {}, ctx.telAct || {});
  numberSet(TOTAL_POWER_ID, totalW, cb);
}

function calcVvxEfficiencyRaw(telM) {
  var t = telM && telM.t ? telM.t : {};
  var den = sget(t, "to_house", 0) - sget(t, "out", 0);
  var effSupply;
  var effExtract;
  var effAvg;

  if (abs(den) < VVX_EFF_DEN_MIN_C) return 0.0;

  effSupply = (sget(t, "post_vvx", 0) - sget(t, "out", 0)) / den;
  effExtract = (sget(t, "to_house", 0) - sget(t, "to_outdoor", 0)) / den;

  effSupply = clip(effSupply, 0, 1);
  effExtract = clip(effExtract, 0, 1);
  effAvg = (effSupply + effExtract) / 2;

  return d1(clip(100 * effAvg, 0, 100));
}

function calcVvxEfficiency(telM, hist) {
  var raw = calcVvxEfficiencyRaw(telM);
  var r0 = hist && typeof hist.r0 === "number" ? hist.r0 : 0;
  var r1 = hist && typeof hist.r1 === "number" ? hist.r1 : r0;

  return {
    pct: clipPct((raw + r0 + r1) / 3),
    hist: { r0: raw, r1: r0, r2: r1 }
  };
}

function applyVvxEfficiencyFeature(ctx, cb) {
  kvsGet(KEY_STATE_HIST, function (hist) {
    var eff = calcVvxEfficiency(ctx.telM || {}, hist || {});
    kvsSet(KEY_STATE_HIST, eff.hist, function () {
      numberSet(VVX_EFFICIENCY_ID, eff.pct, cb);
    });
  });
}

function calcFanAverage(telM, telAct) {
  var sup = telAct && telAct.sup ? telAct.sup : {};
  var ext = telAct && telAct.ext ? telAct.ext : {};
  return clipPct((pct(sup) + pct(ext)) / 2);
}

function applyFanAverageFeature(ctx, cb) {
  var fanAvg = calcFanAverage(ctx.telM || {}, ctx.telAct || {});
  numberSet(FAN_SPEED_AVG_ID, fanAvg, cb);
}
