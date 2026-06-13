// === DEVICE: dampers-8813bfdaa0c0 / SCRIPT: master v0.1.0 ===
// Purpose:
// - Lightweight hub script for lab device.
// - Seeds basic KVS defaults only when missing.
// - Does not run control logic.
(function () {
  "use strict";

  var STATUS_KEY = "hp.master.status";

  var DEFAULTS = [
    { key: "hp.price.area", value: "SE3" },
    { key: "hp.price.status", value: "not_loaded" },
    { key: "hp.price.2h", value: "" },
    { key: "hp.price.date", value: "" },
    { key: "hp.price.updated", value: "" },
    { key: "hp.weather.status", value: "not_loaded" }
  ];

  function log(s) { print("master " + String(s || "")); }

  function kvGet(key, cb) {
    Shelly.call("KVS.Get", { key: key }, function (res, err) {
      if (err || !res) { cb(null); return; }
      cb(res.value);
    });
  }

  function kvSet(key, value, cb) {
    Shelly.call("KVS.Set", { key: key, value: String(value) }, function (res, err) {
      if (err) log("KVS.Set failed " + key + " " + JSON.stringify(err));
      if (cb) cb(!err);
    });
  }

  function seedOne(i) {
    if (i >= DEFAULTS.length) {
      kvSet(STATUS_KEY, "ok", function () { log("ok"); });
      return;
    }

    var d = DEFAULTS[i];
    kvGet(d.key, function (v) {
      if (v === null || v === undefined) {
        kvSet(d.key, d.value, function () { seedOne(i + 1); });
      } else {
        seedOne(i + 1);
      }
    });
  }

  kvSet(STATUS_KEY, "start", function () { seedOne(0); });
})();
