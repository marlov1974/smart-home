#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const fixture = require("./energy_model_fixture");

const sourcePath = path.join(__dirname, "..", "shelly", "energy_pair_v1.js");
const original = fs.readFileSync(sourcePath, "utf8");
const marker = '  publish("starting");\n';
assert(original.includes(marker));

function instrument(stop) {
  const hook = `  globalThis.__model = {
    parse: modelRecord, identity: modelIdentity, one: model1, two: model2,
    candidate: saveCandidate, seed: seedModel, prepare: prepareModels, finish: finish,
    state: function () { return {ready:modelReady, blocked:modelBlocked, final:modelFinal}; }
  };
`;
  return original.replace(marker, hook + (stop ? "  return;\n" : marker));
}

function baseContext(clockRef, call) {
  let timerCallback = null;
  const context = {
    console, print: function () {},
    Timer: {
      set: function (_ms, _repeat, cb) { timerCallback = cb; return 7; },
      clear: function () {}
    },
    Shelly: {
      getComponentStatus: function () { return { unixtime: clockRef.value }; },
      call
    }
  };
  context.globalThis = context;
  context.timer = function () { return timerCallback; };
  return context;
}

// Strict parser: exact UID, field order, ranges, confidence, stability and age.
{
  const clock = { value: 1800000000 };
  const context = baseContext(clock, function () { throw new Error("unexpected RPC"); });
  vm.runInNewContext(instrument(true), context, { filename: sourcePath });
  const uid = "000111112222333344445555";
  const valid = "v=1|api=4|uid=" + uid +
    "|seq=7|a10=1360|sl=3|ss=3600|at=" + (clock.value - 1);
  assert.strictEqual(context.__model.parse(valid, uid, clock.value).gain, 1360);
  for (const bad of [
    valid.replace(uid, "000211112222333344445555"),
    valid.replace("|seq=7|a10=", "|a10=1360|seq=7|a10="),
    valid.replace("|seq=7|", "|seq=65536|"),
    valid.replace("|a10=1360", "|a10=699"),
    valid.replace("|sl=3", "|sl=2"),
    valid.replace("|ss=3600", "|ss=3599"),
    valid.replace(/at=\d+/, "at=" + (clock.value - 15552001)),
    valid + "|bias=-1090"
  ]) assert.strictEqual(context.__model.parse(bad, uid, clock.value), null);

  const m = context.__model.one;
  Object.assign(m, {
    uid, initialGain: 1350, gain: 1360, baseSlopes: 2, slopes: 3,
    stableAt: clock.value - 3600, valid: 0, disabled: 0, savedAt: 0
  });
  const encoded = context.__model.candidate(m, clock.value);
  assert(/^v=1\|api=4\|uid=[0-9a-f]{24}\|seq=1\|a10=1360\|sl=3\|ss=3600\|at=\d+$/.test(encoded));
  assert(!/bias|trim|response|gain1|gain2/.test(encoded));
  m.gain = 1359; assert.strictEqual(context.__model.candidate(m, clock.value), "");
  m.gain = 1360; m.stableAt = clock.value - 3599;
  assert.strictEqual(context.__model.candidate(m, clock.value), "");
  m.stableAt = clock.value - 3600; m.slopes = m.baseSlopes;
  assert.strictEqual(context.__model.candidate(m, clock.value), "");
  m.slopes = 3; m.savedAt = clock.value - 86399;
  assert.strictEqual(context.__model.candidate(m, clock.value), "");
  Object.assign(m, { valid:1, seq:65535, priorSlopes:3, savedGain:1350,
    savedAt:clock.value-90000, stableAt:clock.value-3600 });
  assert.strictEqual(context.__model.candidate(m, clock.value), "");
  let seedResult = 0;
  Object.assign(m, { valid:1, seeded:1, preseeded:1, gain:1350, savedGain:1360, seedDone:0, disabled:0 });
  context.__model.seed(m, x => { seedResult = x; });
  assert.strictEqual(seedResult, 1,
    "a model seeded before this script may already have learned away from its saved gain");
  Object.assign(m, { preseeded:0, seedDone:0 });
  context.__model.seed(m, x => { seedResult = x; });
  assert.strictEqual(seedResult, -1,
    "after this script attempted the seed, a mismatching readback is terminal");
}

// Missing KVS is retried for the complete 30-second startup allowance. No
// model/control write can precede that decision.
{
  const clock = { value: 1800000000 };
  let modelGets = 0, writes = 0, timer;
  const context = baseContext(clock, function (method, args, cb) {
    if (method === "KVS.Set") { cb({}, 0); return; }
    if (method === "KVS.Get" && args.key.indexOf("vp.effect.a.") === 0) {
      modelGets++; cb(null, 1); return;
    }
    if (method === "KVS.Get") { cb(null, 1); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) {
      cb({ values: fixture.identity(args.sid) }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) {
      cb({ values: [4, 0, 1350, 0, 0, 0, 0] }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) {
      cb({ values: [0] }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) {
      cb(null, 1); return;
    }
    if (method === "MbRtuClient.WriteHoldingRegisters") { writes++; cb({}, 0); return; }
    throw new Error("unexpected " + method + " " + args.addr);
  });
  vm.runInNewContext(instrument(false), context, { filename: sourcePath });
  timer = context.timer(); assert(timer);
  assert.strictEqual(context.__model.state().ready, 0);
  for (const seconds of [10, 20]) { clock.value = 1800000000 + seconds; timer(); }
  assert.strictEqual(context.__model.state().ready, 0);
  assert.strictEqual(writes, 0);
  clock.value += 10; timer();
  assert.strictEqual(context.__model.state().ready, 1);
  assert.strictEqual(modelGets, 8);
  assert.strictEqual(writes, 0);
}

// UID words are copied in I78..I83 order. A lost write ACK is recovered by
// readback of schema 4, seed flag and I310 before any EFFECT command.
{
  const epoch = 1800000000;
  const clock = { value: epoch };
  const gain = { 1: 1350, 2: 1350 }, seeded = { 1: 0, 2: 0 };
  const calls = [], seedAttempts = { 1: 0, 2: 0 };
  function uid(sid) { return fixture.identity(sid).slice(6, 12).map(x => x.toString(16).padStart(4, "0")).join(""); }
  function record(sid) {
    return "v=1|api=4|uid=" + uid(sid) + "|seq=4|a10=" + (1360 + sid) +
      "|sl=3|ss=3600|at=" + (epoch - 100);
  }
  const context = baseContext(clock, function (method, args, cb) {
    calls.push({ method, args: JSON.parse(JSON.stringify(args)) });
    if (method === "KVS.Set") { cb({ etag: "status" }, 0); return; }
    if (method === "KVS.Get" && args.key.indexOf("vp.effect.a.") === 0) {
      const sid = args.key === "vp.effect.a." + uid(1) ? 1 : 2;
      cb({ value: record(sid), etag: "e" + sid }, 0); return;
    }
    if (method === "KVS.Get") { cb(null, 1); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) {
      cb({ values: fixture.identity(args.sid) }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) {
      cb({ values: [4, 0, gain[args.sid], 0, 0, 0, 3] }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) {
      cb({ values: [seeded[args.sid]] }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) { cb(null, 1); return; }
    if (method === "MbRtuClient.WriteHoldingRegisters" && args.values[0] === 0xc077) {
      const sid = args.sid; seedAttempts[sid]++;
      assert.deepStrictEqual(Array.from(args.values.slice(2)), fixture.identity(sid).slice(6, 12));
      gain[sid] = args.values[1]; seeded[sid] = 1;
      cb(sid === 1 && seedAttempts[sid] === 1 ? null : {}, sid === 1 && seedAttempts[sid] === 1 ? 1 : 0);
      return;
    }
    if (method === "MbRtuClient.WriteHoldingRegisters") { throw new Error("EFFECT before plan"); }
    throw new Error("unexpected " + method + " " + args.addr);
  });
  vm.runInNewContext(instrument(false), context, { filename: sourcePath });
  assert.strictEqual(context.__model.state().ready, 0, "lost ACK must wait for verification");
  clock.value += 10; context.timer()();
  assert.strictEqual(context.__model.state().ready, 1);
  assert.strictEqual(seedAttempts[1], 1, "readback makes the lost-ACK seed idempotent");
  assert.strictEqual(seedAttempts[2], 1);
  const firstSeed = calls.findIndex(x => x.method === "MbRtuClient.WriteHoldingRegisters");
  assert(calls.slice(0, firstSeed).some(x => x.method === "MbRtuClient.ReadInputRegisters" && x.args.addr === 72));
  assert(calls.slice(firstSeed + 1).some(x => x.method === "MbRtuClient.ReadInputRegisters" && x.args.addr === 346));
}

// A restarted Shelly must also accept a Procon that was seeded earlier in the
// same boot and has since learned a different, still-valid gain.
{
  const epoch = 1800000000, clock = { value: epoch };
  let writes = 0;
  function uid(sid) { return fixture.identity(sid).slice(6, 12).map(x => x.toString(16).padStart(4, "0")).join(""); }
  const context = baseContext(clock, function (method, args, cb) {
    if (method === "KVS.Set") { cb({}, 0); return; }
    if (method === "KVS.Get" && args.key.indexOf("vp.effect.a.") === 0) {
      const sid = args.key === "vp.effect.a." + uid(1) ? 1 : 2;
      cb({ value:"v=1|api=4|uid=" + uid(sid) + "|seq=1|a10=1360|sl=3|ss=3600|at=" + (epoch-1), etag:"e"+sid }, 0); return;
    }
    if (method === "KVS.Get") { cb(null, 1); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) { cb({ values:fixture.identity(args.sid) }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) { cb({ values:[4,0,1420,0,0,0,4] }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) { cb({ values:[1] }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) { cb(null, 1); return; }
    if (method === "MbRtuClient.WriteHoldingRegisters") { writes++; cb({}, 0); return; }
    throw new Error("unexpected " + method + " " + args.addr);
  });
  vm.runInNewContext(instrument(false), context, { filename: sourcePath });
  assert.strictEqual(context.__model.state().ready, 1);
  assert.strictEqual(writes, 0, "restart after learning must neither reseed nor block");
}

// Runtime validation reads identity, record and schema diagnostics but never
// mutates the RAM model with C077.
{
  const epoch = 1800000000, clock = { value: epoch };
  let writes = 0;
  function uid(sid) { return fixture.identity(sid).slice(6, 12).map(x => x.toString(16).padStart(4, "0")).join(""); }
  const context = baseContext(clock, function (method, args, cb) {
    if (method === "KVS.Set") { cb({}, 0); return; }
    if (method === "KVS.Get" && args.key.indexOf("vp.effect.a.") === 0) {
      const sid = args.key === "vp.effect.a." + uid(1) ? 1 : 2;
      cb({ value:"v=1|api=4|uid=" + uid(sid) + "|seq=1|a10=1360|sl=3|ss=3600|at=" + (epoch-1), etag:"e"+sid }, 0); return;
    }
    if (method === "KVS.Get") { cb(null, 1); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) { cb({ values:fixture.identity(args.sid) }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) { cb({ values:[4,0,1350,0,0,0,3] }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) { cb({ values:[0] }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) { cb(null, 1); return; }
    if (method === "MbRtuClient.WriteHoldingRegisters") { writes++; cb({}, 0); return; }
    throw new Error("unexpected " + method + " " + args.addr);
  });
  const validateSource = instrument(false).replace("var VALIDATEONLY = 0;", "var VALIDATEONLY = 1;");
  vm.runInNewContext(validateSource, context, { filename: sourcePath });
  assert.strictEqual(context.__model.state().ready, 1);
  assert.strictEqual(writes, 0);
}

// Both restores complete before model CAS, exact readback and Script.Stop.
{
  const epoch = 1800200000;
  const clock = { value: epoch };
  const log = [], controls = { 1: { state: 4, accepted: 10, saved: 1 }, 2: { state: 4, accepted: 20, saved: 1 } };
  const gain = { 1: 1360, 2: 1370 }, slopes = { 1: 4, 2: 4 };
  let identityFailures = 1;
  const records = {}, etags = {};
  function uid(sid) { return fixture.identity(sid).slice(6, 12).map(x => x.toString(16).padStart(4, "0")).join(""); }
  for (const sid of [1, 2]) {
    const key = "vp.effect.a." + uid(sid);
    records[key] = "v=1|api=4|uid=" + uid(sid) + "|seq=9|a10=1350|sl=3|ss=3600|at=" + (epoch - 90000);
    etags[key] = "old" + sid;
  }
  const context = baseContext(clock, function (method, args, cb) {
    if (method === "KVS.Set" && args.key === "vp.energy.status") { log.push("status"); cb({}, 0); return; }
    if (method === "KVS.Get") {
      log.push("get:" + args.key); cb({ value: records[args.key], etag: etags[args.key] }, 0); return;
    }
    if (method === "KVS.Set") {
      log.push("set:" + args.key); assert.strictEqual(args.etag, etags[args.key]);
      records[args.key] = args.value; etags[args.key] = "new" + args.key.slice(-1);
      cb({ etag: etags[args.key] }, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 256) {
      const c = controls[args.sid], v = new Array(10).fill(0);
      v[0] = c.state; v[1] = c.accepted; v[5] = c.saved; cb({ values: v }, 0); return;
    }
    if (method === "MbRtuClient.WriteHoldingRegisters") {
      assert.strictEqual(args.values[0], 0xc072); log.push("restore:" + args.sid);
      controls[args.sid] = { state: 0, accepted: args.values[1], saved: 0 }; cb({}, 0); return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) {
      if (identityFailures) { identityFailures--; cb(null, 1); }
      else cb({ values: fixture.identity(args.sid) }, 0);
      return;
    }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) { cb({ values: [4, 0, gain[args.sid], 0, 0, 0, slopes[args.sid]] }, 0); return; }
    if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) { cb({ values: [1] }, 0); return; }
    if (method === "Script.Stop") { log.push("stop"); cb({}, 0); return; }
    throw new Error("unexpected " + method + " " + args.addr);
  });
  vm.runInNewContext(instrument(true), context, { filename: sourcePath });
  for (const m of [context.__model.one, context.__model.two]) {
    const sid = m.sid, key = "vp.effect.a." + uid(sid);
    context.__model.identity(m, fixture.identity(sid));
    Object.assign(m, { diag:1, valid:1, raw:records[key], etag:etags[key], seq:9,
      savedGain:1350, savedAt:epoch-90000, priorSlopes:3, initialGain:1350,
      lastGain:gain[sid], gain:gain[sid], baseSlopes:3, slopes:4,
      stableAt:epoch-3600, seeded:1 });
  }
  // Private state is deliberately exposed only by this transformed test source.
  vm.runInNewContext("modelReady=1; busy=0; ending=0; restored1=0; restored2=0;", context);
  context.__model.finish();
  context.__model.finish();
  assert.strictEqual(log.indexOf("stop"), -1, "transient final identity failure is retried after restore");
  context.__model.finish();
  assert.deepStrictEqual(log.filter(x => x.indexOf("restore:") === 0), ["restore:1", "restore:2"]);
  const restore2 = log.indexOf("restore:2");
  const firstSave = log.findIndex(x => x.indexOf("set:vp.effect.a.") === 0);
  const stop = log.indexOf("stop");
  assert(firstSave > restore2 && stop > firstSave);
  assert.strictEqual(log.filter(x => x.indexOf("set:vp.effect.a.") === 0).length, 2);
  for (const value of Object.values(records)) {
    assert(/^v=1\|api=4\|uid=[0-9a-f]{24}\|seq=10\|a10=1[0-9]{3}\|sl=4\|ss=3600\|at=\d+$/.test(value));
  }
}

console.log("PASS UID-bound Shelly gain persistence: strict records, seed readback, gates, CAS and restore ordering");
