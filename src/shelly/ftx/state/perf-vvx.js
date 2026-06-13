// state perf-vvx 1.3.0-classic-calc-rpc-history-write
var VVX_EFFICIENCY_ID = 202;
var KEY_STATE_HIST = "ftx.state.hist";
var VVX_EFF_DEN_MIN_C = 3.0;

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
  return { pct: clipPct((raw + r0 + r1) / 3), hist: { r0: raw, r1: r0, r2: r1 } };
}

function readVvxEfficiencyHist(cb) {
  kvsGet(KEY_STATE_HIST, function (hist) {
    cb(hist || {});
  });
}

function calcVvxEfficiencyFeature(ctx, hist) {
  var eff = calcVvxEfficiency(ctx.telM || {}, hist || {});
  ctx.vvx_eff_pct = eff.pct;
  ctx.vvx_eff_hist = eff.hist;
}

function writeVvxEfficiencyFeature(ctx, cb) {
  kvsSet(KEY_STATE_HIST, ctx.vvx_eff_hist || {}, function () {
    numberSet(VVX_EFFICIENCY_ID, ctx.vvx_eff_pct || 0, cb);
  });
}
