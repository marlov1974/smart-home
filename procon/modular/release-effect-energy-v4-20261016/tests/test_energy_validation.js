#!/usr/bin/env node
"use strict";

// Exercise the real VALIDATEONLY path with the startup condition observed in
// the field: both feedback blocks exist, but their power and age are still the
// unqualified sentinels.  Validation must prove the read/parse/planner path,
// stop itself, and never emit a holding-register write.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const fixture = require("./energy_model_fixture");

const sourcePath = path.join(__dirname, "..", "shelly", "energy_pair_v1.js");
const original = fs.readFileSync(sourcePath, "utf8");
const source = original.replace("var VALIDATEONLY = 0;", "var VALIDATEONLY = 1;");
assert.notStrictEqual(source, original, "validation switch missing");

const epoch = 1800000000;
let clock = epoch;
let timerCallback = null;
let stopped = false;
let writes = 0;
let validated = false;
let modelGets = 0;
const plan = "v=1|rev=1|start=" + epoch + "|q0=1500|q1=1500|q2=1500|q3=1500";

function invalidFeedback() {
  const words = new Array(16).fill(0);
  words[6] = 0x8000;
  words[7] = 0;
  words[15] = 0xffff;
  return words;
}

const context = {
  console,
  print: function () {},
  Timer: {
    set: function (_ms, _repeat, cb) { timerCallback = cb; return 7; },
    clear: function () {}
  },
  Shelly: {
    getComponentStatus: function () { return { unixtime: clock }; },
    call: function (method, args, cb) {
      if (method === "KVS.Set") {
        if (args.key === "vp.energy.status" && args.value.indexOf("phase=validated") >= 0) validated = true;
        cb({}, 0); return;
      }
      if (method === "KVS.Get" && args.key.indexOf("vp.effect.a.") === 0) {
        modelGets++; cb(null, 1); return;
      }
      if (method === "KVS.Get" && args.key === "vp.energy.plan") {
        cb({ value: plan }, 0); return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) {
        cb({ values: fixture.identity(args.sid) }, 0); return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) {
        cb({ values: [4, 0, 1350, 0xffff, 0, 0, 0] }, 0); return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) {
        cb({ values: [0] }, 0); return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) {
        cb({ values: invalidFeedback() }, 0); return;
      }
      if (method === "MbRtuClient.WriteHoldingRegisters") {
        writes++; cb({}, 0); return;
      }
      if (method === "Script.Stop") {
        stopped = true; cb({}, 0); return;
      }
      throw new Error("unexpected RPC " + method + " addr=" + args.addr);
    }
  }
};
context.globalThis = context;
vm.runInNewContext(source, context, { filename: sourcePath });
assert(timerCallback, "validation timer was not installed");
assert.strictEqual(stopped, false, "missing model KVS keeps the 30-second startup allowance");
for (const seconds of [10, 20, 30, 40]) {
  if (stopped) break;
  clock = epoch + seconds;
  timerCallback();
}
assert(modelGets >= 6, "both per-UID model records were retried");
assert(validated, "validated status was not published");
assert(stopped, "VALIDATEONLY did not stop with unready feedback");
assert.strictEqual(writes, 0, "VALIDATEONLY issued a holding-register write");

console.log("PASS energy runtime validation: stale startup feedback, no writes, self-stop");
