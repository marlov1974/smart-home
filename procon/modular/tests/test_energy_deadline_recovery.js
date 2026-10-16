#!/usr/bin/env node
"use strict";

// Execute the production planner with field-derived final-quarter fixtures. RPC writes
// are suppressed by holding the ordinary busy guard while plan() runs.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const sourcePath = path.join(__dirname, "..", "shelly", "energy_pair_v1.js");
let source = fs.readFileSync(sourcePath, "utf8");
const marker = '  publish("starting");\n';
assert(source.includes(marker), "production startup marker missing");

const hook = `  globalThis.__runPlanFixture = function (x) {
    var elapsed = x.elapsed === undefined ? x.t : x.elapsed;
    start = x.t - elapsed; totalWh = x.totalWh; qWh = 0; planReady = 1;
    if (elapsed >= 2700) {
      planQ0 = 4000; planQ1 = 4000; planQ2 = 4000; planQ3 = 4000;
    } else {
      planQ0 = 1500; planQ1 = 2000; planQ2 = 2500; planQ3 = 4000;
    }
    p1 = x.p1; p2 = x.p2; age1 = 0; age2 = 0;
    phase1 = x.phase1 || 3; phase2 = x.phase2 || 3;
    reason1 = x.reason1 || 0; reason2 = x.reason2 || 0;
    commandPair = x.command; plannedPair = x.command; wantedPair = x.command;
    target1 = x.target1; target2 = x.target2;
    sent1 = x.sent1 === undefined ? x.target1 : x.sent1;
    sent2 = x.sent2 === undefined ? x.target2 : x.sent2;
    responseGain1 = 1000; responseGain2 = 1000; cap1 = 12000; cap2 = 12000;
    stable1 = x.t - x.commandAge; stable2 = x.t - x.commandAge;
    lastRetarget = x.t - x.retargetAge;
    lastPlanPower = x.previousPower;
    lastPlanAt = x.t - x.previousAge;
    lastRecovery = x.t - x.recoveryAge;
    busy = 1; ending = 0;
    plan(x.t);
    return {
      wanted: wantedPair, planned: plannedPair, command: commandPair,
      target1: target1, target2: target2, reach: reachPair,
      lastRecovery: lastRecovery, forecastError: forecastErrorWh
    };
  };
  return;
`;
source = source.replace(marker, hook);

const context = {
  console: console,
  print: function () {},
  Shelly: { getComponentStatus: function () { return { unixtime: 0 }; } }
};
context.globalThis = context;
vm.runInNewContext(source, context, { filename: sourcePath });

// Near 05:11 UTC, v1.4.1 credited 12.489 kW for the full five-minute lag
// even though the command was already 10.5 kW. That produced wanted≈7.2 kW
// and the subsequent 9.5 kW command. v1.4.2 must retain the energy demand.
const q7 = context.__runPlanFixture({
  t: 5990, elapsed: 3290, totalWh: 14899, p1: 6037, p2: 6452,
  phase1: 4, reason1: 4, phase2: 3, reason2: 0,
  command: 10500, target1: 5000, target2: 5500,
  previousPower: 12489, previousAge: 30,
  commandAge: 60, retargetAge: 60, recoveryAge: 1000
});
assert(q7.wanted > 12000, "active reduction must lower committed energy");
assert.strictEqual(q7.planned, 12500);
assert.strictEqual(q7.command, 10500, "ordinary dwell remains active");

// The observed 12.489 -> 8.659 kW collapse happened inside that dwell. The
// recovery bypass may apply one 1 kW step, then starts its own 120 s cooldown.
const collapse = context.__runPlanFixture({
  t: 6050, elapsed: 3290, totalWh: 15056, p1: 2490, p2: 6169,
  phase1: 8, reason1: 4, phase2: 2, reason2: 14,
  command: 9500, target1: 4500, target2: 5000,
  previousPower: 12489, previousAge: 60,
  commandAge: 60, retargetAge: 60, recoveryAge: 1000
});
assert.strictEqual(collapse.command, 10500);
assert.strictEqual(collapse.planned, 10500, "recovery is capped to one 1 kW step");
assert.strictEqual(collapse.target1 + collapse.target2, 10500);
assert.deepStrictEqual([collapse.target1, collapse.target2], [3000, 7500]);
assert.strictEqual(collapse.lastRecovery, 6050);

// A normal sub-kW movement cannot bypass dwell, even if the energy planner
// wants a higher command.
const quantized = context.__runPlanFixture({
  t: 6050, elapsed: 3290, totalWh: 14500, p1: 5800, p2: 6000,
  command: 9500, target1: 4500, target2: 5000,
  previousPower: 12489, previousAge: 30,
  commandAge: 30, retargetAge: 30, recoveryAge: 1000
});
assert(quantized.planned > quantized.command);
assert.strictEqual(quantized.command, 9500);

// Even a second real fall cannot create 30-second target chatter while the
// dedicated recovery cooldown is active.
const cooldown = context.__runPlanFixture({
  t: 6080, elapsed: 3290, totalWh: 14500, p1: 2500, p2: 6000,
  command: 10500, target1: 5000, target2: 5500,
  previousPower: 12000, previousAge: 30,
  commandAge: 30, retargetAge: 30, recoveryAge: 30
});
assert(cooldown.planned > cooldown.command);
assert.strictEqual(cooldown.command, 10500);

// A desired split is not yet plant state when one FC16 write failed.  The
// response projection must remain identical to the last successfully sent
// target until that device accepts the retry.
const partialWrite = context.__runPlanFixture({
  t: 100, totalWh: 0, p1: 8000, p2: 3000,
  command: 11000, target1: 8000, target2: 3000,
  sent1: 4000, sent2: 3000,
  previousPower: 11000, previousAge: 30,
  commandAge: 30, retargetAge: 30, recoveryAge: 1000
});
const acceptedReference = context.__runPlanFixture({
  t: 100, totalWh: 0, p1: 8000, p2: 3000,
  command: 11000, target1: 4000, target2: 3000,
  sent1: 4000, sent2: 3000,
  previousPower: 11000, previousAge: 30,
  commandAge: 30, retargetAge: 30, recoveryAge: 1000
});
assert.strictEqual(partialWrite.wanted, acceptedReference.wanted);
assert.strictEqual(partialWrite.forecastError, acceptedReference.forecastError);

console.log("PASS energy deadline projection and bounded collapse recovery");
