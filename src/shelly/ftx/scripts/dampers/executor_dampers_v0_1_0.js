// executor_dampers_v0_1_0
var SCRIPT_ID = 4;
var KEY = "ftx.intent.dev.dmp";
var DEVICE = "dmp";
var SWITCH_ID = 0;
var MAX_AGE_S = 300;

function log(m) { print(String(m)); }
function n(v, d) { var x = Number(v); return (x === x) ? x : d; }
function b(v) { return v ? 1 : 0; }
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
    var cur = st && st["switch:" + SWITCH_ID] ? st["switch:" + SWITCH_ID] : {};
    var desiredOn = b(x.act.on);
    var curOn = b(cur.output);
    if (curOn === desiredOn) {
      log("EX dmp noop");
      selfStop();
      return;
    }
    Shelly.call("Switch.Set", { id: SWITCH_ID, on: !!desiredOn }, function (res2, err2) {
      if (err2) log("EX dmp err");
      else log("EX dmp " + desiredOn);
      selfStop();
    });
  });
}
fetchIntent(function (x) {
  if (!validIntent(x)) {
    log("EX dmp skip");
    selfStop();
    return;
  }
  applyIntent(x);
});
