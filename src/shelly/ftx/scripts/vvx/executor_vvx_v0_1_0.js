// executor_vvx_v0_2_0-local-thermal
var SCRIPT_ID = 10;
var KEY = "ftx.intent.dev.vvx";
var DEVICE = "vvx";
var SWITCH_ID = 0;
var MAX_AGE_S = 300;
var TEMP_BAND_C = 0.2;
var HELP_MARGIN_C = 0.3;

function log(m) { print(String(m)); }
function n(v, d) { var x = Number(v); return (x === x) ? x : d; }
function isNum(v) { return typeof v === "number" && v === v; }
function b(v) { return v ? 1 : 0; }
function selfStop() { Timer.set(80, false, function () { Shelly.call("Script.Stop", { id: SCRIPT_ID }, function () {}); }); }
function nowS() { return Math.floor((new Date()).getTime() / 1000); }
function validIntent(x) {
  var age;
  if (!x || typeof x !== "object") return 0;
  if (x.device !== DEVICE || x.driver_inhibit) return 0;
  age = nowS() - n(x.ts, 0);
  if (age < -60 || age > MAX_AGE_S) return 0;
  return x.act && typeof x.act === "object";
}
function decideOn(x) {
  var target = x.target_to_house_c;
  var temp = x.temp || {};
  var out = temp.out_c;
  var house = temp.house_c;

  if (!b(x.act.on)) return { on: 0, reason: "deny" };
  if (!isNum(target) || !isNum(out) || !isNum(house)) return { on: 0, reason: "nodata" };

  if (target < house - TEMP_BAND_C) {
    return { on: out > house + HELP_MARGIN_C ? 1 : 0, reason: "cool" };
  }
  if (target > house + TEMP_BAND_C) {
    return { on: out < house - HELP_MARGIN_C ? 1 : 0, reason: "heat" };
  }
  return { on: 0, reason: "hold" };
}
function applyIntent(x) {
  Shelly.call("Shelly.GetStatus", {}, function (st, err) {
    var cur = st && st["switch:" + SWITCH_ID] ? st["switch:" + SWITCH_ID] : {};
    var decision = decideOn(x);
    var desiredOn = decision.on;
    var curOn = b(cur.output);
    if (curOn === desiredOn) {
      log("EX vvx noop " + decision.reason);
      selfStop();
      return;
    }
    Shelly.call("Switch.Set", { id: SWITCH_ID, on: !!desiredOn }, function (res2, err2) {
      if (err2) log("EX vvx err");
      else log("EX vvx " + desiredOn + " " + decision.reason);
      selfStop();
    });
  });
}
Shelly.call("KVS.Get", { key: KEY }, function (res, err) {
  var x = (!err && res) ? res.value : null;
  if (!validIntent(x)) {
    log("EX vvx skip");
    selfStop();
    return;
  }
  applyIntent(x);
});
