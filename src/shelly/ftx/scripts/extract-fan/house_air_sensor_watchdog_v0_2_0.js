// house_air_sensor_watchdog_v0_2_0
(function () {
  "use strict";

  var TAG = "house_air_wd";
  var TEMP_KEY = "temperature:105";
  var RH_KEY = "humidity:105";
  var SWITCH_ID = 100;
  var EXECUTOR_ID = 3;
  var CHECK_MS = 60000;
  var EXEC_MS = 43000;
  var OFF_MS = 10000;
  var cycling = 0;

  function log(s) {
    print(TAG + " " + String(s || ""));
  }

  function hasErrors(comp) {
    return !!(comp && comp.errors && comp.errors.length);
  }

  function badScalar(v) {
    var s;
    if (v === null || v === undefined) return 1;
    if (typeof v === "number") return (v !== v || v === 0) ? 1 : 0;
    if (typeof v === "string") {
      s = v.toLowerCase();
      return (s === "" || s === "n/a" || s === "na" || s === "null" || Number(v) === 0) ? 1 : 0;
    }
    return 1;
  }

  function badComponent(status, key, field) {
    var comp = status ? status[key] : null;
    if (!comp || hasErrors(comp)) return 1;
    return badScalar(comp[field]);
  }

  function describe(status, key, field) {
    var comp = status ? status[key] : null;
    if (!comp) return "missing";
    if (hasErrors(comp)) return "err";
    if (comp[field] === null || comp[field] === undefined) return "null";
    return String(comp[field]);
  }

  function startExecutor() {
    Shelly.call("Script.Start", { id: EXECUTOR_ID }, function (res, err) {
      if (err) log("ERR exec");
    });
  }

  function setSensorPower(onValue, cb) {
    Shelly.call("Switch.Set", { id: SWITCH_ID, on: !!onValue }, function (res, err) {
      if (err) log("ERR switch " + (onValue ? "on" : "off"));
      if (cb) cb(err ? 0 : 1);
    });
  }

  function cycleSensor(reason) {
    if (cycling) {
      log("SKIP cycling");
      return;
    }
    cycling = 1;
    log("CYCLE " + reason);
    setSensorPower(0, function () {
      Timer.set(OFF_MS, false, function () {
        setSensorPower(1, function () {
          cycling = 0;
          log("ON");
        });
      });
    });
  }

  function checkSensor() {
    if (cycling) {
      log("SKIP check");
      return;
    }
    Shelly.call("Shelly.GetStatus", {}, function (status, err) {
      var badT;
      var badRh;
      var tDesc;
      var rhDesc;
      if (err || !status) {
        log("ERR status");
        return;
      }
      badT = badComponent(status, TEMP_KEY, "tC");
      badRh = badComponent(status, RH_KEY, "rh");
      tDesc = describe(status, TEMP_KEY, "tC");
      rhDesc = describe(status, RH_KEY, "rh");
      if (badT || badRh) {
        cycleSensor("t=" + tDesc + " rh=" + rhDesc);
        return;
      }
      log("OK t=" + tDesc + " rh=" + rhDesc);
    });
  }

  log("BOT");
  Timer.set(9000, false, startExecutor);
  Timer.set(15000, false, checkSensor);
  Timer.set(EXEC_MS, true, startExecutor);
  Timer.set(CHECK_MS, true, checkSensor);
}());
