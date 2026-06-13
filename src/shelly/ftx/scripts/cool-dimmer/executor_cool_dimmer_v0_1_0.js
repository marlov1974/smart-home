// executor_cool_dimmer_v0_1_0
var SCRIPT_ID = 2;
var KEY = "ftx.intent.dev.cool";
var KEY_THERMAL = "ftx.tel.thermal.cool";
var DEVICE = "cool";
var LIGHT_ID = 0;
var MAX_AGE_S = 300;
var STEP_PCT = 5;
var HOLD_BAND_C = 0.2;

function log(m) { print(String(m)); }
function n(v, d) { var x = Number(v); return (x === x) ? x : d; }
function i(v) { var x = Number(v); if (x !== x) return 0; return Math.floor(x + 0.5); }
function isNum(v) { return typeof v === "number" && v === v; }
function b(v) { return v ? 1 : 0; }
function clip(v, lo, hi) { var x = n(v, 0); if (x < lo) x = lo; if (x > hi) x = hi; return x; }
function clipPct(v) { return i(clip(v, 0, 100)); }
function selfStop() { Timer.set(80, false, function () { Shelly.call("Script.Stop", { id: SCRIPT_ID }, function () {}); }); }
function nowS() { return Math.floor((new Date()).getTime() / 1000); }
function fetchIntent(cb) {
  Shelly.call("KVS.Get", { key: KEY }, function (res, err) {
    cb((!err && res) ? res.value : null);
  });
}
function validIntent(x) {
  var age;
  if (!x || typeof x !== "object") return 0;
  if (x.device !== DEVICE || x.driver_inhibit) return 0;
  age = nowS() - n(x.ts, 0);
  if (age < -60 || age > MAX_AGE_S) return 0;
  return x.act && typeof x.act === "object";
}
function readThermal(cb) {
  Shelly.call("KVS.Get", { key: KEY_THERMAL }, function (res, err) {
    cb((!err && res && res.value && typeof res.value === "object") ? res.value : {});
  });
}
function targetPct(x, thermal, curPct) {
  var target = x && x.act ? x.act.target_to_house_c : null;
  var toHouse = thermal ? thermal.to_house : null;
  var fallback = x && x.act && isNum(x.act.pct) ? clipPct(x.act.pct) : curPct;
  var e;
  if (!b(x.act.on)) return 0;
  if (!isNum(target) || !isNum(toHouse)) return fallback;
  e = toHouse - target;
  if (e > HOLD_BAND_C) return clipPct(curPct + STEP_PCT);
  if (e < -HOLD_BAND_C) return clipPct(curPct - STEP_PCT);
  return curPct;
}
function applyIntent(x) {
  Shelly.call("Shelly.GetStatus", {}, function (st, err) {
    var cur = st && st["light:" + LIGHT_ID] ? st["light:" + LIGHT_ID] : {};
    var curOn = b(cur.output);
    var curPct = clipPct(cur.brightness);
    readThermal(function (thermal) {
      var desiredPct = targetPct(x, thermal, curPct);
      var desiredOn = desiredPct > 0 ? 1 : 0;
      if (curOn === desiredOn && curPct === desiredPct) {
        log("EX cool noop");
        selfStop();
        return;
      }
      Shelly.call("Light.Set", { id: LIGHT_ID, on: !!desiredOn, brightness: desiredPct }, function (res2, err2) {
        if (err2) log("EX cool err");
        else log("EX cool " + desiredPct);
        selfStop();
      });
    });
  });
}
fetchIntent(function (x) {
  if (!validIntent(x)) {
    log("EX cool skip");
    selfStop();
    return;
  }
  applyIntent(x);
});
