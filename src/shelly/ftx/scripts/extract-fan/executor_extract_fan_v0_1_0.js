// executor_extract_fan_v0_1_0
var SCRIPT_ID = 3;
var KEY = "ftx.intent.dev.ext";
var DEVICE = "ext";
var LIGHT_ID = 0;
var MAX_AGE_S = 300;

function log(m) { print(String(m)); }
function n(v, d) { var x = Number(v); return (x === x) ? x : d; }
function i(v) { var x = Number(v); if (x !== x) return 0; return Math.floor(x + 0.5); }
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
function applyIntent(x) {
  Shelly.call("Shelly.GetStatus", {}, function (st, err) {
    var cur = st && st["light:" + LIGHT_ID] ? st["light:" + LIGHT_ID] : {};
    var desiredOn = b(x.act.on);
    var desiredPct = desiredOn ? clipPct(x.act.pct) : 0;
    var curOn = b(cur.output);
    var curPct = clipPct(cur.brightness);
    if (curOn === desiredOn && curPct === desiredPct) {
      log("EX ext noop");
      selfStop();
      return;
    }
    Shelly.call("Light.Set", { id: LIGHT_ID, on: !!desiredOn, brightness: desiredPct }, function (res2, err2) {
      if (err2) log("EX ext err");
      else log("EX ext " + desiredPct);
      selfStop();
    });
  });
}
fetchIntent(function (x) {
  if (!validIntent(x)) {
    log("EX ext skip");
    selfStop();
    return;
  }
  applyIntent(x);
});
