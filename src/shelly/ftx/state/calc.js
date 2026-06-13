// state calc 1.0.0
function sget(o, a, d) {
  if (o && typeof o[a] === "number") return o[a];
  return d;
}

function on(o) {
  return o && o.on ? 1 : 0;
}

function pct(o) {
  return sget(o, "pct", 0);
}

function w(o) {
  return sget(o, "w", 0);
}

function calcRun(telM, telAct) {
  var sup = telAct && telAct.sup ? telAct.sup : {};
  var ext = telAct && telAct.ext ? telAct.ext : {};
  var vvx = telAct && telAct.vvx ? telAct.vvx : {};
  var heat = telAct && telAct.heat ? telAct.heat : {};
  var cool = telAct && telAct.cool ? telAct.cool : {};
  var dmp = telAct && telAct.dmp ? telAct.dmp : {};
  var rpm = telM && telM.rpm ? telM.rpm : {};
  var pa = telM && telM.pa ? telM.pa : {};
  var t = telM && telM.t ? telM.t : {};

  return {
    sup: b(on(sup) && pct(sup) > 10 && sget(rpm, "sup", 0) > FAN_RPM_RUN_MIN && sget(pa, "sup", 0) >= FAN_DP_RUN_MIN_PA),
    ext: b(on(ext) && pct(ext) > 10 && sget(rpm, "ext", 0) > FAN_RPM_RUN_MIN && sget(pa, "ext", 0) >= FAN_DP_RUN_MIN_PA),
    vvx: b(on(vvx) && sget(rpm, "vvx", 0) > VVX_RPM_RUN_MIN),
    heat: b(on(heat) && pct(heat) > 0 && (sget(t, "to_house", 0) - sget(t, "post_vvx", 0)) >= HEAT_DT_MIN_C),
    cool: b(on(cool) && pct(cool) > 0 && (sget(t, "post_vvx", 0) - sget(t, "to_house", 0)) >= COOL_DT_MIN_C),
    dmp: b(on(dmp))
  };
}

function calcVvxRaw(telM) {
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

function calcPerf(telM, telAct, hist) {
  var sup = telAct && telAct.sup ? telAct.sup : {};
  var ext = telAct && telAct.ext ? telAct.ext : {};
  var vvx = telAct && telAct.vvx ? telAct.vvx : {};
  var heat = telAct && telAct.heat ? telAct.heat : {};
  var cool = telAct && telAct.cool ? telAct.cool : {};
  var dmp = telAct && telAct.dmp ? telAct.dmp : {};
  var raw = calcVvxRaw(telM);
  var r0 = hist && typeof hist.r0 === "number" ? hist.r0 : 0;
  var r1 = hist && typeof hist.r1 === "number" ? hist.r1 : r0;
  var eff = clipPct((raw + r0 + r1) / 3);
  var total = IDLE_POWER_W + (on(dmp) ? DAMPERS_POWER_W : 0) + w(sup) + w(ext) + w(vvx) + w(heat) + w(cool);
  var fanAvg = clipPct((pct(sup) + pct(ext)) / 2);

  return {
    total_w: i(clip(total, 0, 9999)),
    vvx_eff_pct: eff,
    fan_avg_pct: fanAvg,
    hist: { r0: raw, r1: r0, r2: r1 }
  };
}
