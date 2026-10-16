#!/usr/bin/env node
"use strict";

// End-to-end exercise of the production KVS-plan path. RPC callbacks are
// synchronous here, but the ordinary telemetry, plan refresh, command and
// restoration functions run unchanged.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const modelFixture = require("./energy_model_fixture");

const sourcePath = path.join(__dirname, "..", "shelly", "energy_pair_v1.js");
let source = fs.readFileSync(sourcePath, "utf8");
const marker = '  publish("starting");\n';
assert(source.includes(marker), "production startup marker missing");
const hook = `  globalThis.__planState = function () {
    return {
      ready: planReady, revision: planRevision, raw: planRaw,
      state: planState, start: start,
      q0: planQ0, q1: planQ1, q2: planQ2, q3: planQ3,
      qWh: qWh, totalWh: totalWh, assumedWh: assumedWh, debtWh: debtWh,
      unknownS: unknownS,
      command: commandPair, sent1: sent1, sent2: sent2,
      ending: ending
    };
  };\n`;
source = source.replace(marker, hook + marker);

const epoch = 1800000000; // exactly divisible by 900
let clock = epoch + 100;
let planValue = null;
let timerCallback = null;
let stopped = false;
const writes = [];
const statuses = [];
const controls = {
  1: { state: 0, accepted: 0, saved: 0 },
  2: { state: 0, accepted: 0, saved: 0 }
};

function feedbackWords(power) {
  const words = new Array(16).fill(0);
  const unsigned = power >>> 0;
  words[0] = 3;
  words[6] = (unsigned >>> 16) & 0xffff;
  words[7] = unsigned & 0xffff;
  words[15] = 0;
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
      if (method === "KVS.Set") {
        statuses.push(args.value);
        assert(Buffer.byteLength(args.value) < 254, "status exceeds Shelly KVS value limit");
        callback({}, 0); return;
      }
      if (method === "KVS.Get") {
        if (planValue === null) callback(null, 1);
        else callback({ value: planValue }, 0);
        return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) {
        callback({ values: feedbackWords(3000) }, 0); return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 256) {
        const ctl = controls[args.sid];
        const values = new Array(10).fill(0);
        values[0] = ctl.state; values[1] = ctl.accepted; values[5] = ctl.saved;
        callback({ values: values }, 0); return;
      }
      if (method === "MbRtuClient.WriteHoldingRegisters") {
        const ctl = controls[args.sid];
        const restore = args.values[0] === 0xc072;
        ctl.accepted = args.values[1];
        ctl.state = restore ? 0 : 4;
        ctl.saved = restore ? 0 : 1;
        writes.push({ at: clock, sid: args.sid, restore: restore, target: args.values[3] });
        callback({}, 0); return;
      }
      if (method === "Script.Stop") { stopped = true; callback({}, 0); return; }
      throw new Error("unexpected RPC " + method + " addr=" + args.addr);
    }
  }
};
context.globalThis = context;
vm.runInNewContext(source, context, { filename: sourcePath });
assert(timerCallback, "production timer was not installed");

// Missing KVS at startup is a passive waiting state. Fresh telemetry alone is
// not authority to create an EFFECT session.
assert.strictEqual(context.__planState().ready, 0);
assert.strictEqual(context.__planState().state, 2);
assert.strictEqual(writes.length, 0);

const first = "v=1|rev=1|start=" + epoch + "|q0=2000|q1=2000|q2=2500|q3=4000";
assert(Buffer.byteLength(first) < 254);
planValue = first;
clock = epoch + 130;
timerCallback();
let accepted = context.__planState();
assert.strictEqual(accepted.ready, 1);
assert.strictEqual(accepted.revision, 1);
assert.deepStrictEqual([accepted.q0, accepted.q1, accepted.q2, accepted.q3],
  [2000, 2000, 2500, 4000]);
assert(Math.abs(accepted.assumedWh - 2000 * accepted.unknownS / 900) < 0.001,
  "unknown pre-start interval must be prorated, not treated as zero delivery");
assert.strictEqual(accepted.unknownS, 130,
  "the whole elapsed part of q0 is unknown until the first plan is accepted");
assert.strictEqual(writes.length, 2, "first valid plan should create one pair session");

// A malformed higher revision cannot partially replace the active scalars.
planValue = "v=1|rev=2|start=" + epoch + "|q0=6000|q1=bad|q2=6000|q3=6000";
clock = epoch + 160;
timerCallback();
let invalid = context.__planState();
assert.strictEqual(invalid.revision, 1);
assert.strictEqual(invalid.raw, first);
assert.strictEqual(invalid.state, 3);
assert.deepStrictEqual([invalid.q0, invalid.q1, invalid.q2, invalid.q3],
  [2000, 2000, 2500, 4000]);

// The same revision with different contents is a conflict, not an in-place
// mutation. A missing read likewise retains the complete accepted plan.
planValue = "v=1|rev=1|start=" + epoch + "|q0=6000|q1=6000|q2=6000|q3=6000";
clock = epoch + 190;
timerCallback();
assert.strictEqual(context.__planState().state, 5);
assert.strictEqual(context.__planState().raw, first);
planValue = null;
clock = epoch + 220;
timerCallback();
assert.strictEqual(context.__planState().state, 2);
assert.strictEqual(context.__planState().revision, 1);

// Keep normal sampling intervals while approaching the boundary; this makes
// the carried deficit independently calculable from measured 6 kW output.
for (let offset = 250; offset <= 820; offset += 30) {
  clock = epoch + offset;
  timerCallback();
}

// A next-quarter plan may be staged early. It remains unapplied until its
// declared boundary, then rolls atomically without restoring the EFFECT lease.
const rolled = "v=1|rev=3|start=" + (epoch + 900) +
  "|q0=2000|q1=2500|q2=3000|q3=3500";
planValue = rolled;
clock = epoch + 850;
timerCallback();
assert.strictEqual(context.__planState().revision, 1);
assert.strictEqual(context.__planState().state, 6);
const restoreBeforeRoll = writes.filter(function (w) { return w.restore; }).length;
clock = epoch + 905;
timerCallback();
const afterRoll = context.__planState();
assert.strictEqual(afterRoll.revision, 3);
assert.strictEqual(afterRoll.start, epoch + 900);
assert.deepStrictEqual([afterRoll.q0, afterRoll.q1, afterRoll.q2, afterRoll.q3],
  [2000, 2500, 3000, 3500]);
assert.strictEqual(afterRoll.totalWh, afterRoll.qWh,
  "new horizon must retain only energy observed since its boundary");
assert(afterRoll.debtWh > 400 && afterRoll.debtWh < 500,
  "completed underdelivery must carry into the next horizon exactly once");
assert(Math.abs(afterRoll.debtWh) <= 6000, "carried error must remain bounded");
assert.strictEqual(writes.filter(function (w) { return w.restore; }).length, restoreBeforeRoll,
  "quarter roll must not restore or recreate native mode");
assert(afterRoll.sent1 >= 3000 && afterRoll.sent2 >= 3000,
  "existing EFFECT sessions remain owned across the roll");

// With no successor at the end of the accepted four-quarter horizon, restore
// both devices. The second tick observes the completed restores and stops.
planValue = null;
clock = epoch + 900 + 4 * 900 + 1;
timerCallback();
assert.strictEqual(context.__planState().ending, 1);
timerCallback();
assert(stopped, "expired plan must finish restoration and stop");
assert.strictEqual(writes.filter(function (w) { return w.restore; }).length,
  restoreBeforeRoll + 2);
assert(statuses.length > 0);

console.log("PASS rolling KVS energy plan: passive wait, atomic revisions, roll and expiry restore");
