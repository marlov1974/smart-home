#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const modelFixture = require("./energy_model_fixture");

const sourcePath = path.join(__dirname, "..", "shelly", "energy_pair_v1.js");
let source = fs.readFileSync(sourcePath, "utf8");
const marker = '  publish("starting");\n';
const hook = `  globalThis.__clockState = function () {
    return {ready: clockReady, start: start, lastAt: lastAt,
      unknownS: unknownS, qUnknownS: qUnknownS, totalWh: totalWh,
      assumedWh: assumedWh, revision: planRevision, sent1: sent1, sent2: sent2};
  };\n`;
assert(source.includes(marker));
source = source.replace(marker, hook + marker);

const epoch = 1800000000;
let clock = 0;
let timerCallback = null;
const writes = [];
const statuses = [];
const controls = {
  1: { state: 0, accepted: 0, saved: 0 },
  2: { state: 0, accepted: 0, saved: 0 }
};
const planValue = "v=1|rev=9|start=" + epoch +
  "|q0=2000|q1=2000|q2=2000|q3=2000";

function feedbackWords() {
  const words = new Array(16).fill(0);
  words[0] = 3; words[7] = 3000; words[15] = 0;
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
        assert(Buffer.byteLength(args.value) < 254);
        callback({}, 0); return;
      }
      if (method === "KVS.Get") { callback({ value: planValue }, 0); return; }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 321) {
        callback({ values: feedbackWords() }, 0); return;
      }
      if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 256) {
        const ctl = controls[args.sid];
        const values = new Array(10).fill(0);
        values[0] = ctl.state; values[1] = ctl.accepted; values[5] = ctl.saved;
        callback({ values: values }, 0); return;
      }
      if (method === "MbRtuClient.WriteHoldingRegisters") {
        const ctl = controls[args.sid];
        ctl.state = 4; ctl.saved = 1; ctl.accepted = args.values[1];
        writes.push({ at: clock, sid: args.sid, target: args.values[3] });
        callback({}, 0); return;
      }
      if (method === "Script.Stop") { callback({}, 0); return; }
      throw new Error("unexpected RPC " + method);
    }
  }
};
context.globalThis = context;
vm.runInNewContext(source, context, { filename: sourcePath });
assert(timerCallback);

// Shelly can report unixtime=0 before NTP. This must remain a passive clock
// wait: no KVS plan is accepted and no device command is written.
assert.strictEqual(context.__clockState().ready, false);
assert.strictEqual(context.__clockState().revision, 0);
assert.strictEqual(writes.length, 0);

clock = epoch + 100;
timerCallback();
let synced = context.__clockState();
assert.strictEqual(synced.ready, true);
assert.strictEqual(synced.start, epoch);
assert.strictEqual(synced.revision, 9);
assert.strictEqual(synced.unknownS, 100);
assert(Math.abs(synced.assumedWh - 2000 * 100 / 900) < 0.001);
assert.strictEqual(writes.length, 2);

// A backward correction does not integrate negative time or issue a new
// target. The next interval starts with an unqualified endpoint.
const totalBeforeBackstep = synced.totalWh;
clock = epoch + 90;
timerCallback();
const backed = context.__clockState();
assert.strictEqual(backed.lastAt, clock);
assert.strictEqual(backed.totalWh, totalBeforeBackstep);
assert.strictEqual(writes.length, 2);

// A large forward jump is recorded as unknown, never as epoch-sized energy.
// Holding the already accepted targets is allowed; no retarget is inferred.
clock = epoch + 490;
timerCallback();
const jumped = context.__clockState();
assert.strictEqual(jumped.lastAt, clock);
assert.strictEqual(jumped.totalWh, totalBeforeBackstep);
assert(jumped.unknownS >= 500 && jumped.unknownS < 1000);
assert(jumped.sent1 >= 3000 && jumped.sent2 >= 3000);

console.log("PASS energy clock gate: zero epoch, backstep and forward jump are not integrated");
