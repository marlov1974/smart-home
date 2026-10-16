/* P0080 pair energy executor 1.5.1. KVS rolling four-quarter plan. */
(function () {
  "use strict";

  var SID1 = 1, SID2 = 2, CID = 100;
  var QSEC = 900, QCOUNT = 4, TICKMS = 10000, PLANSEC = 30;
  var LEASE = 180, MAXFLOW = 5500, MAXPAIR = 24000;
  var FLOORPAIR = 6000, RESPONSESEC = 300, COLLAPSEW = 1500, RECOVERYSTEP = 1000;
  var PLANKEY = "vp.energy.plan", PLANVER = 1;
  var MINQWH = FLOORPAIR * QSEC / 3600, MAXQWH = MAXPAIR * QSEC / 3600;
  var MINUNIX = 1600000000, MAXCLOCKGAP = 300, MAXDEBTWH = 6000;
  var PAIRUP = 2000 / 300, PAIRDOWN = 1250 / 300;
  var VALIDATEONLY = 0;
  var MAGIC = 0xc076, EFFECT = 5, VERSION = 3;
  var bootAt = Shelly.getComponentStatus("sys").unixtime;
  var clockReady = bootAt >= MINUNIX;
  var start = clockReady ? Math.floor(bootAt / QSEC) * QSEC : 0;
  var lastAt = clockReady ? bootAt : 0, lastP1 = -1, lastP2 = -1, lastFresh1 = 0, lastFresh2 = 0;
  var totalWh = 0, qWh = 0, unknownS = clockReady ? bootAt - start : 0, qUnknownS = unknownS;
  var assumedWh = 0, debtWh = 0;
  var p1 = 0, p2 = 0, age1 = 999, age2 = 999;
  var phase1 = 0, phase2 = 0, reason1 = 0, reason2 = 0;
  var commandPair = 6000, plannedPair = 6000, wantedPair = 6000, reachPair = 24000, shortfall = 0;
  var forecastErrorWh = 0;
  var target1 = 3000, target2 = 3000, sent1 = -1, sent2 = -1;
  var responseGain1 = 1000, responseGain2 = 1000, cap1 = 12000, cap2 = 12000;
  var stable1 = start, stable2 = start, splitLead = 1, lastRetarget = start - 120;
  var lastPlanPower = -1, lastPlanAt = 0, lastRecovery = start - 120;
  var owned1 = 0, owned2 = 0, busy = 0, ending = 0, restored1 = 0, restored2 = 0;
  var cycle = 0, lastPlan = 0, lastWrite1 = 0, lastWrite2 = 0;
  var q0 = 0, q1 = 0, q2 = 0, q3 = 0;
  var planReady = 0, planRevision = 0, planRaw = "", planState = 0, lastPlanRead = 0;
  var planQ0 = 0, planQ1 = 0, planQ2 = 0, planQ3 = 0;
  var stagedReady = 0, stagedRevision = 0, stagedStart = 0, stagedRaw = "";
  var stagedQ0 = 0, stagedQ1 = 0, stagedQ2 = 0, stagedQ3 = 0;

  function now() { return Shelly.getComponentStatus("sys").unixtime; }
  function abs(x) { return x < 0 ? -x : x; }
  function clip(x, lo, hi) { if (x < lo) return lo; if (x > hi) return hi; return x; }
  function round500(x) { return Math.floor((x + 250) / 500) * 500; }
  function cap500(x) { return clip(Math.floor(x / 500) * 500, 3000, 12000); }
  function s32(hi, lo) { var x = hi * 65536 + lo; return x >= 2147483648 ? x - 4294967296 : x; }
  function qTargetWh(q) {
    if (q === 0) return planQ0;
    if (q === 1) return planQ1;
    if (q === 2) return planQ2;
    if (q === 3) return planQ3;
    return 0;
  }
  function cumulativeTargetWh(q) {
    if (q < 0) return 0;
    if (q === 0) return planQ0;
    if (q === 1) return planQ0 + planQ1;
    if (q === 2) return planQ0 + planQ1 + planQ2;
    return planQ0 + planQ1 + planQ2 + planQ3;
  }
  function qSave(q, wh) {
    if (q === 0) q0 = wh; else if (q === 1) q1 = wh; else if (q === 2) q2 = wh;
    else if (q === 3) q3 = wh;
  }
  function status(phase) {
    return "v=3|phase=" + phase + "|q=" + Math.floor((now() - start) / QSEC) +
      "|r=" + planRevision + "|s=" + start + "|x=" + planState +
      "|qwh=" + Math.floor(qWh + 0.5) + "|totalwh=" + Math.floor(totalWh + 0.5) +
      "|a=" + Math.floor(assumedWh + 0.5) + "|d=" + Math.floor(debtWh + 0.5) +
      "|p1=" + p1 + "|p2=" + p2 + "|want=" + Math.floor(wantedPair) +
      "|cmd=" + commandPair + "|sent=" + (sent1 < 0 || sent2 < 0 ? 0 : sent1 + sent2) + "|reach=" + reachPair +
      "|shortw=" + Math.floor(shortfall) + "|ferr=" + Math.floor(forecastErrorWh) +
      "|lim=" + phase1 + "/" + reason1 + "," +
      phase2 + "/" + reason2 + "|unknown=" + unknownS +
      "|results=" + Math.floor(q0 + 0.5) + "," + Math.floor(q1 + 0.5) + "," +
      Math.floor(q2 + 0.5) + "," + Math.floor(q3 + 0.5);
  }
  function publish(phase, cb) {
    Shelly.call("KVS.Set", { key: "vp.energy.status", value: status(phase) }, cb || function () {});
  }
  function uintAt(s, first, last, maximum) {
    var i, c, value = 0;
    if (last <= first || last - first > 10) return -1;
    if (last - first > 1 && s.charCodeAt(first) === 48) return -1;
    for (i = first; i < last; i++) {
      c = s.charCodeAt(i) - 48;
      if (c < 0 || c > 9) return -1;
      value = value * 10 + c;
      if (value > maximum) return -1;
    }
    return value;
  }
  function installPlan(raw, rev, planStart, v0, v1, v2, v3, t) {
    var resetAccounting = !planReady || planStart !== start;
    var completed, oldObjective, oldDelivered, elapsedUnknown;
    if (resetAccounting) {
      if (planReady) {
        completed = Math.floor((planStart - start) / QSEC);
        completed = clip(completed, 1, QCOUNT);
        oldObjective = cumulativeTargetWh(completed - 1) + debtWh;
        oldDelivered = totalWh + assumedWh - qWh;
        debtWh = clip(oldObjective - oldDelivered, -MAXDEBTWH, MAXDEBTWH);
      } else debtWh = 0;
      start = planStart; totalWh = qWh; unknownS = qUnknownS;
      elapsedUnknown = Math.min(qUnknownS, Math.max(0, t - planStart));
      assumedWh = v0 * elapsedUnknown / QSEC;
      q0 = 0; q1 = 0; q2 = 0; q3 = 0;
    }
    planQ0 = v0; planQ1 = v1; planQ2 = v2; planQ3 = v3;
    planRevision = rev; planRaw = raw; planReady = 1; planState = 1;
    if (stagedReady && rev >= stagedRevision) stagedReady = 0;
    lastPlan = 0;
    print("ENERGY PLAN rev=" + rev + " start=" + planStart +
      " wh=" + v0 + "," + v1 + "," + v2 + "," + v3);
  }
  function activateStaged(t) {
    if (!stagedReady || t < stagedStart ||
        Math.floor(t / QSEC) * QSEC !== stagedStart) return 0;
    installPlan(stagedRaw, stagedRevision, stagedStart,
      stagedQ0, stagedQ1, stagedQ2, stagedQ3, t);
    stagedReady = 0;
    return 1;
  }
  function acceptPlan(raw, t) {
    var a, b, rev, planStart, v0, v1, v2, v3, currentStart, acceptedRevision;
    if (typeof raw !== "string" || raw.length < 48 || raw.length > 120 ||
        raw.substr(0, 8) !== "v=" + PLANVER + "|rev=") { planState = 3; return 0; }
    if (planReady && raw === planRaw) { planState = 1; return 1; }
    if (stagedReady && raw === stagedRaw) { planState = 6; return 1; }
    a = 8; b = raw.indexOf("|start=", a); rev = uintAt(raw, a, b, 2147483647);
    if (b < 0) { planState = 3; return 0; }
    a = b + 7; b = raw.indexOf("|q0=", a); planStart = uintAt(raw, a, b, 4294967295);
    if (b < 0) { planState = 3; return 0; }
    a = b + 4; b = raw.indexOf("|q1=", a); v0 = uintAt(raw, a, b, MAXQWH);
    if (b < 0) { planState = 3; return 0; }
    a = b + 4; b = raw.indexOf("|q2=", a); v1 = uintAt(raw, a, b, MAXQWH);
    if (b < 0) { planState = 3; return 0; }
    a = b + 4; b = raw.indexOf("|q3=", a); v2 = uintAt(raw, a, b, MAXQWH);
    if (b < 0) { planState = 3; return 0; }
    a = b + 4; v3 = uintAt(raw, a, raw.length, MAXQWH);
    if (rev < 1 || planStart < MINUNIX || planStart % QSEC !== 0 ||
        v0 < MINQWH || v1 < MINQWH || v2 < MINQWH || v3 < MINQWH) {
      planState = 3; return 0;
    }
    acceptedRevision = planRevision;
    if (stagedReady && stagedRevision > acceptedRevision) acceptedRevision = stagedRevision;
    if ((planReady || stagedReady) && rev < acceptedRevision) { planState = 4; return 0; }
    if ((planReady || stagedReady) && rev === acceptedRevision) { planState = 5; return 0; }
    currentStart = Math.floor(t / QSEC) * QSEC;
    if (t >= planStart + QCOUNT * QSEC) { planState = 7; return 0; }
    if (planStart === currentStart + QSEC) {
      stagedRevision = rev; stagedStart = planStart; stagedRaw = raw;
      stagedQ0 = v0; stagedQ1 = v1; stagedQ2 = v2; stagedQ3 = v3;
      stagedReady = 1; planState = 6;
      return 1;
    }
    if (planStart !== currentStart && !(planReady && planStart === start)) {
      planState = 6; return 0;
    }
    // All validation precedes installPlan.  The executor observes either the
    installPlan(raw, rev, planStart, v0, v1, v2, v3, t);
    return 1;
  }
  function refreshPlan(t, cb) {
    lastPlanRead = t;
    Shelly.call("KVS.Get", { key: PLANKEY }, function (r, e) {
      if (e || !r || typeof r.value !== "string") planState = 2;
      else acceptPlan(r.value, t);
      cb();
    });
  }
  function read(sid, addr, qty, cb) {
    Shelly.call("MbRtuClient.ReadInputRegisters", { id: CID, sid: sid, addr: addr, qty: qty, timeout: 5 },
      function (r, e) { if (e || !r || !r.values) cb(null); else cb(r.values); });
  }
  var MODELAGE = 15552000, MODELDAY = 86400, MODELKEY = "vp.effect.a.";
  var modelBegan = 0, modelReady = 0, modelBlocked = 0, lastModelSample = 0, modelFinal = 0, modelFinalAt = 0;
  var model1 = { sid: SID1 }, model2 = { sid: SID2 };
  function hex4(x) { var s = x.toString(16); return "0000".substr(s.length) + s; }
  function modelIdentity(m, v) {
    var raw;
    if (!v || v.length !== 15) return 0;
    if (v[0] !== 1 || v[1] !== m.sid || v[2] !== m.sid || v[3] !== 3 ||
        v[4] !== 1 || v[5] !== 1 || v[13] !== 1 || v[14] !== 0) return -1;
    raw = v[12];
    if (raw < 0 || raw > 255 || (raw & 0x60) !== 0x60 || (raw & 31) !== m.sid) return -1;
    if ((v[6] === 0 && v[7] === 0 && v[8] === 0 && v[9] === 0 && v[10] === 0 && v[11] === 0) ||
        (v[6] === 65535 && v[7] === 65535 && v[8] === 65535 && v[9] === 65535 &&
         v[10] === 65535 && v[11] === 65535)) return -1;
    m.u0 = v[6]; m.u1 = v[7]; m.u2 = v[8]; m.u3 = v[9]; m.u4 = v[10]; m.u5 = v[11];
    m.uid = hex4(m.u0) + hex4(m.u1) + hex4(m.u2) + hex4(m.u3) + hex4(m.u4) + hex4(m.u5);
    m.key = MODELKEY + m.uid; m.identity = 1; return 1;
  }
  function modelRecord(raw, uid, t) {
    var prefix = "v=1|api=4|uid=" + uid + "|seq=", a, b, seq, gain, slopes, stable, at;
    if (typeof raw !== "string" || raw.length < prefix.length + 35 || raw.length > 160 ||
        raw.substr(0, prefix.length) !== prefix) return null;
    a = prefix.length; b = raw.indexOf("|a10=", a); seq = uintAt(raw, a, b, 65535);
    if (b < 0) return null;
    a = b + 5; b = raw.indexOf("|sl=", a); gain = uintAt(raw, a, b, 2000);
    if (b < 0) return null;
    a = b + 4; b = raw.indexOf("|ss=", a); slopes = uintAt(raw, a, b, 65535);
    if (b < 0) return null;
    a = b + 4; b = raw.indexOf("|at=", a); stable = uintAt(raw, a, b, 4294967295);
    if (b < 0) return null;
    at = uintAt(raw, b + 4, raw.length, 4294967295);
    if (seq < 1 || gain < 700 || slopes < 3 || stable < 3600 ||
        at < MINUNIX || at > t || t - at > MODELAGE) return null;
    return { seq: seq, gain: gain, slopes: slopes, stable: stable, at: at };
  }
  function loadModel(m, t, cb) {
    if (m.loaded) { cb(); return; }
    if (m.next && t < m.next) { cb(); return; }
    Shelly.call("KVS.Get", { key: m.key }, function (r, e) {
      var x;
      if (e || !r || typeof r.value !== "string") {
        if (t - modelBegan < 30) { m.next = t + 5; cb(); return; }
        m.loaded = 1; cb(); return;
      }
      m.raw = r.value; m.etag = typeof r.etag === "string" ? r.etag : "";
      x = modelRecord(m.raw, m.uid, t); m.loaded = 1;
      if (x) { m.valid = 1; m.seq = x.seq; m.savedGain = x.gain; m.priorSlopes = x.slopes; m.savedAt = x.at; }
      cb();
    });
  }
  function modelDiag(m, initial, cb) {
    read(m.sid, 308, 7, function (v) {
      if (!v || v[0] !== 4 || v[2] < 700 || v[2] > 2000) { cb(0); return; }
      read(m.sid, 346, 1, function (s) {
        if (!s || s[0] > 1) { cb(0); return; }
        if (initial && !m.diag) {
          m.initialGain = v[2]; m.lastGain = v[2]; m.baseSlopes = v[6];
          m.stableAt = now(); m.diag = 1; m.seeded = s[0]; m.preseeded = s[0];
        }
        m.gain = v[2]; m.slopes = v[6]; m.seeded = s[0]; cb(1);
      });
    });
  }
  function seedModel(m, cb) {
    if (!m.valid || m.seedDone || m.disabled) { cb(1); return; }
    if (VALIDATEONLY) { m.seedDone = 1; cb(1); return; }
    if (m.seeded) {
      if (m.preseeded || m.gain === m.savedGain) { m.seedDone = 1; cb(1); }
      else cb(-1);
      return;
    }
    if (!m.seedAt) m.seedAt = now();
    Shelly.call("MbRtuClient.WriteHoldingRegisters", { id: CID, sid: m.sid, addr: 300,
      values: [0xc077, m.savedGain, m.u0, m.u1, m.u2, m.u3, m.u4, m.u5], timeout: 5 },
      function (r, e) {
        if (e) { cb(now() - m.seedAt >= 30 ? -1 : 0); return; }
        modelDiag(m, 0, function (ok) {
          if (ok && m.seeded === 1 && m.gain === m.savedGain) { m.seedDone = 1; cb(1); return; }
          cb(now() - m.seedAt >= 30 ? -1 : 0);
        });
      });
  }
  function prepareModels(t, cb) {
    if (modelReady) { cb(1); return; }
    if (modelBlocked) { cb(-1); return; }
    if (t < MINUNIX) { cb(0); return; }
    if (!modelBegan) modelBegan = t;
    function loaded() {
      if (!model1.loaded || !model2.loaded) { cb(0); return; }
      modelDiag(model1, 1, function (a) {
        if (!a) { modelBlocked = 1; cb(-1); return; }
        modelDiag(model2, 1, function (b) {
          if (!b) { modelBlocked = 1; cb(-1); return; }
          seedModel(model1, function (c) {
            if (c < 0) { modelBlocked = 1; cb(-1); return; }
            if (!c) { cb(0); return; }
            seedModel(model2, function (d) {
              if (d < 0) { modelBlocked = 1; cb(-1); return; }
              if (!d) { cb(0); return; }
              modelReady = 1; lastModelSample = t; cb(1);
            });
          });
        });
      });
    }
    function loads() {
      loadModel(model1, t, function () { loadModel(model2, t, loaded); });
    }
    if (!model1.identity || !model2.identity) {
      read(SID1, 72, 15, function (a) {
        var x = modelIdentity(model1, a);
        if (x < 0) { modelBlocked = 1; cb(-1); return; }
        if (!x) { cb(0); return; }
        read(SID2, 72, 15, function (b) {
          x = modelIdentity(model2, b);
          if (x < 0 || (x > 0 && model1.uid === model2.uid)) { modelBlocked = 1; cb(-1); return; }
          if (!x) { cb(0); return; }
          loads();
        });
      });
    } else loads();
  }
  function observeModel(m, t, cb) {
    modelDiag(m, 0, function (ok) {
      if (!ok) { cb(0); return; }
      if (m.gain !== m.lastGain) { m.lastGain = m.gain; m.stableAt = t; }
      cb(1);
    });
  }
  function sampleModels(t, force, cb) {
    if (!modelReady || (!force && t - lastModelSample < 60)) { cb(1); return; }
    lastModelSample = t;
    observeModel(model1, t, function (a) {
      if (!a) { cb(0); return; }
      observeModel(model2, t, cb);
    });
  }
  function saveCandidate(m, t) {
    var delta = m.slopes >= m.baseSlopes ? m.slopes - m.baseSlopes : 0;
    var confidence = m.valid ? m.priorSlopes + delta : m.slopes;
    var reference = m.valid ? m.savedGain : m.initialGain;
    if (m.disabled || !delta || confidence < 3 || t - m.stableAt < 3600 ||
        (m.valid && m.seq >= 65535) ||
        abs(m.gain - reference) < 10 || (m.savedAt && t - m.savedAt < MODELDAY)) return "";
    if (confidence > 65535) confidence = 65535;
    m.confidence = confidence;
    m.nextSeq = m.valid ? m.seq + 1 : 1;
    return "v=1|api=4|uid=" + m.uid + "|seq=" + m.nextSeq + "|a10=" + m.gain +
      "|sl=" + confidence + "|ss=" + (t - m.stableAt) + "|at=" + t;
  }
  function saveModel(m, t, cb) {
    var value = saveCandidate(m, t);
    if (!value) { cb(1); return; }
    Shelly.call("KVS.Get", { key: m.key }, function (r, e) {
      var p;
      if (!e && r && typeof r.value === "string") {
        if (!m.etag || r.etag !== m.etag || r.value !== m.raw) { cb(1); return; }
        p = { key: m.key, value: value, etag: m.etag };
      } else {
        if (m.etag || m.raw) { cb(0); return; }
        p = { key: m.key, value: value };
      }
      Shelly.call("KVS.Set", p, function (w, we) {
        if (we || !w || typeof w.etag !== "string") { cb(0); return; }
        Shelly.call("KVS.Get", { key: m.key }, function (q, qe) {
          if (!qe && q && q.value === value && q.etag === w.etag) {
            m.raw = value; m.etag = q.etag; m.valid = 1; m.seq = m.nextSeq;
            m.savedGain = m.gain; m.savedAt = t; m.priorSlopes = m.confidence;
            m.baseSlopes = m.slopes; m.saved = 1;
            cb(1); return;
          }
          cb(qe || !q ? 0 : 1);
        });
      });
    });
  }
  function finalResult(cb, terminal) {
    if (terminal || now() - modelFinalAt >= 30) { modelFinal = 1; cb(1); }
    else cb(0);
  }
  function finalizeModels(cb) {
    if (modelFinal) { cb(1); return; }
    var t = now();
    if (!modelFinalAt) modelFinalAt = t;
    read(SID1, 72, 15, function (a) {
      var check1 = { sid: SID1 }, one = modelIdentity(check1, a);
      if (one !== 1) { finalResult(cb, one < 0); return; }
      read(SID2, 72, 15, function (b) {
        var check2 = { sid: SID2 }, two = modelIdentity(check2, b);
        if (two !== 1 || check1.uid !== model1.uid || check2.uid !== model2.uid) {
          finalResult(cb, two < 0 || two === 1); return;
        }
        sampleModels(t, 1, function (sampled) {
          if (!sampled) { finalResult(cb, 0); return; }
          saveModel(model1, t, function (saved1) {
            if (!saved1) { finalResult(cb, 0); return; }
            saveModel(model2, t, function (saved2) { finalResult(cb, saved2); });
          });
        });
      });
    });
  }

  function feedback(sid, cb) {
    read(sid, 321, 16, function (v) {
      if (!v) { cb(-1, 999, 0, 0); return; }
      var w = s32(v[6], v[7]);
      cb(w === -2147483648 ? -1 : w, v[15], v[0], v[1]);
    });
  }
  function initializeClock(t, fresh1, fresh2) {
    clockReady = true; start = Math.floor(t / QSEC) * QSEC; lastAt = t;
    totalWh = 0; qWh = 0; unknownS = t - start; qUnknownS = unknownS;
    assumedWh = 0; debtWh = 0;
    lastP1 = p1; lastP2 = p2; lastFresh1 = fresh1; lastFresh2 = fresh2;
    stable1 = t; stable2 = t; lastRetarget = t - 120; lastRecovery = t - 120;
  }
  function discardClockInterval(t) {
    var dt = t - lastAt, oldq, newq, currentStart;
    if (dt > 0) {
      unknownS += dt;
      oldq = Math.floor((lastAt - start) / QSEC);
      newq = Math.floor((t - start) / QSEC);
      if (newq > oldq) {
        qSave(oldq, qWh); qWh = 0;
        qUnknownS = Math.max(0, t - (start + newq * QSEC));
      } else qUnknownS += dt;
    }
    if (!planReady) {
      currentStart = Math.floor(t / QSEC) * QSEC;
      start = currentStart; totalWh = 0; qWh = 0;
      unknownS = t - currentStart; qUnknownS = unknownS;
      assumedWh = 0; debtWh = 0;
    }
    lastAt = t; lastP1 = p1; lastP2 = p2; lastFresh1 = 0; lastFresh2 = 0;
    planState = 8;
  }
  function integrate(t) {
    var dt = t - lastAt;
    if (dt <= 0) return;
    var fresh1 = p1 >= 0 && age1 < 60, fresh2 = p2 >= 0 && age2 < 60;
    var valid1 = dt < 60 && fresh1 && lastFresh1;
    var valid2 = dt < 60 && fresh2 && lastFresh2;
    var oldq = Math.floor((lastAt - start) / QSEC), newq = Math.floor((t - start) / QSEC);
    var beforeWh = 0, afterWh = 0;
    if (newq > oldq && oldq >= 0 && oldq < QCOUNT) {
      var cut = start + (oldq + 1) * QSEC, beforeS = cut - lastAt, afterS = t - cut;
      var f = beforeS / dt, mid;
      if (valid1) {
        mid = lastP1 + (p1 - lastP1) * f;
        beforeWh += (lastP1 + mid) * 0.5 * beforeS / 3600;
        afterWh += (mid + p1) * 0.5 * afterS / 3600;
      }
      if (valid2) {
        mid = lastP2 + (p2 - lastP2) * f;
        beforeWh += (lastP2 + mid) * 0.5 * beforeS / 3600;
        afterWh += (mid + p2) * 0.5 * afterS / 3600;
      }
      var carriedWh = afterWh;
      totalWh += beforeWh + carriedWh; qWh += beforeWh; qSave(oldq, qWh); qWh = carriedWh;
      qUnknownS = (!valid1 || !valid2) ? afterS : 0;
    } else {
      if (valid1) beforeWh += (lastP1 + p1) * 0.5 * dt / 3600;
      if (valid2) beforeWh += (lastP2 + p2) * 0.5 * dt / 3600;
      totalWh += beforeWh; qWh += beforeWh;
    }
    if (!valid1 || !valid2) {
      unknownS += dt;
      if (newq === oldq) qUnknownS += dt;
    }
    if (!planReady && newq > oldq) {
      start = Math.floor(t / QSEC) * QSEC;
      if (newq - oldq > 1 || dt >= 60) { qWh = 0; qUnknownS = t - start; }
      totalWh = qWh; unknownS = qUnknownS;
      q0 = 0; q1 = 0; q2 = 0; q3 = 0;
    }
    lastAt = t; lastP1 = p1; lastP2 = p2; lastFresh1 = fresh1; lastFresh2 = fresh2;
  }
  function learnResponseGain(t, p, age, ph, why, sent, stable, gain) {
    if (ph !== 3 || why !== 0 || age >= 60 || p < 0 || sent < 3000 || t - stable < 180) return gain;
    return (7 * gain + clip(p * 1000 / sent, 650, 1150)) / 8;
  }
  function thermalLimiter(ph, why) {
    return (why === 4 || why === 15) && (ph === 4 || ph === 7 || ph === 8);
  }
  function committedEnd(actual, target, limited, changing) {
    if (limited) return 0;
    if (!changing) return actual;
    return Math.min(actual, target);
  }
  function updateCapability(p, age, ph, why, cap) {
    if (p < 0 || age >= 60) return cap;
    if (thermalLimiter(ph, why)) return clip(p + 500, 3000, 12000);
    return clip(cap + 500, 3000, 12000);
  }
  function splitCommand(t) {
    var low = Math.floor(commandPair / 1000) * 500, high = commandPair - low;
    var c1 = cap500(cap1), c2 = cap500(cap2);
    target1 = low; target2 = high;
    if (high !== low) {
      if (responseGain1 + 25 < responseGain2) { target1 = high; target2 = low; }
      else if (responseGain2 + 25 < responseGain1) { target1 = low; target2 = high; }
      else {
        if (splitLead === 1) { target1 = high; target2 = low; splitLead = 2; }
        else { target1 = low; target2 = high; splitLead = 1; }
      }
    }
    if (target1 > c1) { target2 += target1 - c1; target1 = c1; }
    if (target2 > c2) { target1 += target2 - c2; target2 = c2; }
  }
  function plan(t) {
    var elapsed = t - start, q = Math.floor(elapsed / QSEC), into = elapsed - q * QSEC;
    if (q >= QCOUNT) { finish(); return; }
    var remain = QSEC - into, lag = Math.min(RESPONSESEC, remain);
    var active = Math.max(0, remain - lag);
    var actualPower = (p1 >= 0 ? p1 : 0) + (p2 >= 0 ? p2 : 0);
    var limited1 = thermalLimiter(phase1, reason1), limited2 = thermalLimiter(phase2, reason2);
    var limited = limited1 || limited2;
    var responseStart = committedEnd(p1, sent1 >= 3000 ? sent1 : target1, limited1,
      t - stable1 < RESPONSESEC) + committedEnd(p2, sent2 >= 3000 ? sent2 : target2, limited2,
      t - stable2 < RESPONSESEC);
    var committed = (actualPower + responseStart) * 0.5 * lag / 3600;
    var objective = cumulativeTargetWh(q) + debtWh;
    var required = (objective - totalWh - assumedWh - committed) * 3600 / Math.max(30, active);
    var nextRequired = required;
    if (q + 1 < QCOUNT) nextRequired =
      (cumulativeTargetWh(q + 1) + debtWh - totalWh - assumedWh - committed) *
      3600 / Math.max(30, remain + QSEC - lag);
    var prep = clip((into - (QSEC - 2 * RESPONSESEC)) / (2 * RESPONSESEC), 0, 1);
    var nextWeight = 1 + 3 * prep;
    cap1 = updateCapability(p1, age1, phase1, reason1, cap1);
    cap2 = updateCapability(p2, age2, phase2, reason2, cap2);
    reachPair = cap500(cap1) + cap500(cap2);
    var deadlineMaxEnd = Math.min(reachPair, responseStart + PAIRUP * active);
    var deadlineMinEnd = Math.max(Math.min(FLOORPAIR, responseStart),
      responseStart - PAIRDOWN * active);
    var maxAverage = (responseStart + deadlineMaxEnd) / 2;
    var minAverage = (responseStart + deadlineMinEnd) / 2;
    if (required > maxAverage || required < minAverage) wantedPair = nextRequired;
    else wantedPair = (required + nextWeight * nextRequired) / (1 + nextWeight);
    wantedPair = clip(wantedPair, FLOORPAIR, reachPair);
    shortfall = Math.max(0, required - maxAverage);
    var forecastEnd = clip(wantedPair, deadlineMinEnd, deadlineMaxEnd);
    var forecastAverage = (responseStart + forecastEnd) / 2;
    forecastErrorWh = totalWh + assumedWh + committed + forecastAverage * active / 3600 - objective;
    var rawCommand = wantedPair * 2000 / (responseGain1 + responseGain2);
    rawCommand = clip(rawCommand, commandPair - 1000, commandPair + 2000);
    plannedPair = round500(clip(rawCommand, FLOORPAIR, reachPair));
    var limitedDown = plannedPair < commandPair && limited;
    var planDt = lastPlanAt ? Math.max(0, t - lastPlanAt) : 0;
    var collapse = lastPlanPower >= 0 && plannedPair > commandPair &&
      actualPower + 500 < commandPair &&
      lastPlanPower - actualPower > PAIRDOWN * Math.min(RESPONSESEC, planDt) + COLLAPSEW &&
      t - lastRecovery >= 120;
    var recovery = collapse && t - lastRetarget < 120;
    if (recovery) plannedPair = Math.min(plannedPair, commandPair + RECOVERYSTEP);
    if (plannedPair !== commandPair && (limitedDown || recovery || t - lastRetarget >= 120)) {
      commandPair = plannedPair; lastRetarget = t; splitCommand(t);
      if (recovery) lastRecovery = t;
    }
    lastPlanPower = actualPower; lastPlanAt = t;
    print("ENERGY q=" + q + " into=" + into + " wh=" + Math.floor(qWh) +
      " req=" + Math.floor(required) + " want=" + Math.floor(wantedPair) +
      " cmd=" + commandPair + " split=" + target1 + "+" + target2 +
      " actual=" + actualPower + " reach=" + reachPair + " short=" + Math.floor(shortfall) +
      " ferr=" + Math.floor(forecastErrorWh));
    if (VALIDATEONLY) {
      publish("validated", function () {
        Timer.clear(timer); Shelly.call("Script.Stop", { id: 7 }, function () {});
      });
      return;
    }
    commandBoth();
  }
  function nextSeq(a) { return a >= 65535 ? 1 : a + 1; }
  function commandOne(sid, target, cb) {
    read(sid, 256, 10, function (c) {
      if (!c) { cb(0); return; }
      var st = c[0], saved = c[5], accepted = c[1];
      if (ending) {
        if (st === 0 && saved === 0) { cb(2); return; }
        if (!saved || (st !== 4 && st !== 6)) { cb(0); return; }
        Shelly.call("MbRtuClient.WriteHoldingRegisters", { id: CID, sid: sid, addr: 300,
          values: [0xc072, nextSeq(accepted), 1, 0, 0, 0, 0, 2], timeout: 5 }, function (r, e) { cb(e ? 0 : 1); });
        return;
      }
      if (st === 3 || st === 5) { cb(0); return; }
      if (st !== 0 && st !== 4) { cb(0); return; }
      Shelly.call("MbRtuClient.WriteHoldingRegisters", { id: CID, sid: sid, addr: 300,
        values: [MAGIC, nextSeq(accepted), EFFECT, target, MAXFLOW, LEASE, 1, VERSION], timeout: 5 },
        function (r, e) { cb(e ? 0 : 1); });
    });
  }
  function commandBoth() {
    if (busy || ending) return;
    busy = 1;
    commandOne(SID1, target1, function (ok1) {
      if (ok1) {
        if (sent1 !== target1) stable1 = now();
        owned1 = 1; sent1 = target1; lastWrite1 = now();
      }
      commandOne(SID2, target2, function (ok2) {
        if (ok2) {
          if (sent2 !== target2) stable2 = now();
          owned2 = 1; sent2 = target2; lastWrite2 = now();
        }
        busy = 0; publish("running");
      });
    });
  }
  function renewHeld() {
    if (busy || ending || sent1 < 0 || sent2 < 0) return;
    var hold1 = sent1, hold2 = sent2;
    busy = 1;
    commandOne(SID1, hold1, function (ok1) {
      if (ok1) { owned1 = 1; sent1 = hold1; lastWrite1 = now(); }
      commandOne(SID2, hold2, function (ok2) {
        if (ok2) { owned2 = 1; sent2 = hold2; lastWrite2 = now(); }
        busy = 0; publish("holding");
      });
    });
  }
  function restoreLoop() {
    if (busy) return;
    busy = 1;
    commandOne(SID1, 0, function (r1) {
      if (r1 === 2) restored1 = 1;
      commandOne(SID2, 0, function (r2) {
        if (r2 === 2) restored2 = 1;
        if (restored1 && restored2) {
          finalizeModels(function (done) {
            busy = 0;
            if (done) {
              publish("complete"); print("ENERGY COMPLETE " + status("complete"));
              Timer.clear(timer); Shelly.call("Script.Stop", { id: 7 }, function () {});
            }
          });
        } else busy = 0;
      });
    });
  }
  function finish() {
    if (!ending) {
      ending = 1; publish("restoring");
    }
    restoreLoop();
  }
  function afterPlanRefresh(t, fresh1, fresh2, w1, w2, a1, a2) {
    busy = 0;
    if (!planReady) { publish("waiting"); return; }
    if (t - start >= QCOUNT * QSEC) { finish(); return; }
    // Runtime validation must also finish when freshly flashed firmware has
    // not produced its first qualified power pair yet.  It has already read
    // both identities, model diagnostics, feedback blocks and the complete
    // plan.  plan() publishes the proof and stops before commandBoth().
    if (VALIDATEONLY) { lastPlan = t; plan(t); return; }
    if (!fresh1 || !fresh2) {
      if (sent1 >= 0 && sent2 >= 0 &&
          (t - lastWrite1 >= 55 || t - lastWrite2 >= 55)) {
        print("ENERGY HOLD telemetry p=" + w1 + "/" + w2 + " age=" + a1 + "/" + a2 +
          " cmd=" + commandPair + " split=" + target1 + "+" + target2);
        renewHeld();
      }
      return;
    }
    if (t - lastPlan >= PLANSEC || t - lastWrite1 >= 55 || t - lastWrite2 >= 55) {
      lastPlan = t; plan(t);
    }
  }
  function tick() {
    if (busy) return;
    if (ending) { restoreLoop(); return; }
    busy = 1;
    prepareModels(now(), function (modelState) {
      if (modelState !== 1) {
        busy = 0; publish(modelState < 0 ? "identity" : "modelwait"); return;
      }
      feedback(SID1, function (w1, a1, ph1, why1) {
        feedback(SID2, function (w2, a2, ph2, why2) {
        var t = now();
        var fresh1 = w1 >= 0 && a1 < 60, fresh2 = w2 >= 0 && a2 < 60;
        p1 = w1; p2 = w2; age1 = a1; age2 = a2;
        if (t < MINUNIX) {
          planState = 8; cycle++; busy = 0; publish("clock"); return;
        }
        if (!clockReady) initializeClock(t, fresh1, fresh2);
        else if (t < lastAt || t - lastAt > MAXCLOCKGAP) {
          discardClockInterval(t); fresh1 = 0; fresh2 = 0;
        } else {
          responseGain1 = learnResponseGain(t, w1, a1, ph1, why1, sent1, stable1, responseGain1);
          responseGain2 = learnResponseGain(t, w2, a2, ph2, why2, sent2, stable2, responseGain2);
          integrate(t);
        }
        if (fresh1) { phase1 = ph1; reason1 = why1; }
        if (fresh2) { phase2 = ph2; reason2 = why2; }
        if (stagedReady) activateStaged(t);
        cycle++;
          sampleModels(t, 0, function () {
            if (!planReady || t - lastPlanRead >= PLANSEC) {
              refreshPlan(t, function () { afterPlanRefresh(t, fresh1, fresh2, w1, w2, a1, a2); });
            } else afterPlanRefresh(t, fresh1, fresh2, w1, w2, a1, a2);
          });
        });
      });
    });
  }
  publish("starting");
  var timer = Timer.set(TICKMS, true, tick);
  tick();
})();
