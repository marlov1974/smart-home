#!/usr/bin/env node
"use strict";

// Execute the production Shelly script with synchronous RPC mocks.  This is
// intentionally an end-to-end script test: the ordinary tick, integration,
// planning, split and lease-renewal paths all run unchanged.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const modelFixture = require("./energy_model_fixture");

const sourcePath = path.join(__dirname, "..", "shelly", "energy_pair_v1.js");
let source = fs.readFileSync(sourcePath, "utf8");
const marker = '  publish("starting");\n';
assert(source.includes(marker), "production startup marker missing");

const hook = `  globalThis.__energyTest = {
    tick: tick,
    state: function () {
      return {
        p1: p1, p2: p2, age1: age1, age2: age2,
        totalWh: totalWh, unknownS: unknownS,
        commandPair: commandPair, target1: target1, target2: target2,
        sent1: sent1, sent2: sent2, lastPlan: lastPlan,
        lastWrite1: lastWrite1, lastWrite2: lastWrite2, cycle: cycle
      };
    }
  };\n`;
source = source.replace(marker, hook + marker);

const epoch = 1800000000;
let clock = epoch + 100;
let planValue = "v=1|rev=1|start=" + epoch + "|q0=1500|q1=2000|q2=2500|q3=4000";
let timerCallback = null;
let failFeedbackSid = 0;
const writes = [];
const controls = {
  1: { state: 0, accepted: 0, saved: 0 },
  2: { state: 0, accepted: 0, saved: 0 }
};

function feedbackWords(power, age) {
  const words = new Array(16).fill(0);
  const unsigned = power >>> 0;
  words[0] = 3; // ACTIVE
  words[1] = 0; // no limiter
  words[6] = (unsigned >>> 16) & 0xffff;
  words[7] = unsigned & 0xffff;
  words[15] = age;
  return words;
}

const context = {
  console: console,
  print: function () {},
  Timer: {
    set: function (_ms, _repeat, callback) { timerCallback = callback; return 1; },
    clear: function () {}
  },
  Shelly: {
    getComponentStatus: function () { return { unixtime: clock }; },
    call: function (method, args, callback) {
      if (modelFixture.respond(method, args, callback)) return;
      if (method === "KVS.Set") { callback({}, 0); return; }
      if (method === "KVS.Get") { callback({ value: planValue }, 0); return; }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) {
        if (failFeedbackSid === args.sid) {
          failFeedbackSid = 0;
          callback(null, 1);
        } else {
          callback({ values: feedbackWords(3000, 0) }, 0);
        }
        return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 256) {
        const ctl = controls[args.sid];
        const values = new Array(10).fill(0);
        values[0] = ctl.state;
        values[1] = ctl.accepted;
        values[5] = ctl.saved;
        callback({ values: values }, 0);
        return;
      }
      if (method === "MbRtuClient.WriteHoldingRegisters") {
        const ctl = controls[args.sid];
        ctl.state = 4;
        ctl.accepted = args.values[1];
        ctl.saved = 1;
        writes.push({ at: clock, sid: args.sid, target: args.values[3] });
        callback({}, 0);
        return;
      }
      if (method === "Script.Stop") { callback({}, 0); return; }
      throw new Error("unexpected RPC " + method + " addr=" + args.addr);
    }
  }
};
context.globalThis = context;
vm.runInNewContext(source, context, { filename: sourcePath });
assert(timerCallback, "production timer was not installed");

const initial = context.__energyTest.state();
assert.strictEqual(initial.sent1 + initial.sent2, initial.commandPair);
assert.strictEqual(writes.length, 2);

// Make the planning window and the 55-second lease-renewal margin expire,
// then lose one feedback RPC.  The active command may be renewed, but it must
// not be replanned from an invented zero-power sample.
clock = epoch + 230;
failFeedbackSid = 1;
timerCallback();
const held = context.__energyTest.state();
assert.strictEqual(held.p1, -1);
assert.strictEqual(held.commandPair, initial.commandPair);
assert.deepStrictEqual([held.target1, held.target2], [initial.target1, initial.target2]);
assert.strictEqual(held.lastPlan, initial.lastPlan);
assert.strictEqual(held.unknownS, initial.unknownS + 130);
assert.strictEqual(writes.length, 4, "existing pair should be lease-renewed");
assert.deepStrictEqual(writes.slice(-2).map(function (w) { return w.target; }),
  [initial.target1, initial.target2]);
assert.deepStrictEqual([held.lastWrite1, held.lastWrite2], [clock, clock]);

// A fresh pair immediately replans because the failed tick did not consume
// the planning deadline.  The interval touching the failed endpoint remains
// explicitly unknown.
clock = epoch + 240;
timerCallback();
const recovered = context.__energyTest.state();
assert.deepStrictEqual([recovered.p1, recovered.p2], [3000, 3000]);
assert.deepStrictEqual([recovered.age1, recovered.age2], [0, 0]);
assert.strictEqual(recovered.lastPlan, clock);
assert(recovered.commandPair > held.commandPair, "fresh feedback should permit the pending retarget");
assert.strictEqual(recovered.target1 + recovered.target2, recovered.commandPair);
assert.strictEqual(recovered.unknownS, initial.unknownS + 140);

// The following fresh interval is integrated normally: no restart and no
// lingering telemetry latch.
clock = epoch + 250;
timerCallback();
const following = context.__energyTest.state();
assert(following.totalWh > recovered.totalWh);
assert.strictEqual(following.unknownS, recovered.unknownS);
assert.strictEqual(following.cycle, recovered.cycle + 1);

console.log("PASS energy transient feedback: hold, lease renewal, unknown accounting and fresh recovery");
