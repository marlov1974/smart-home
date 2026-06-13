// === DEVICE: dampers-8813bfdaa0c0 / SCRIPT: weather v0.1.0 ===
// Purpose:
// - Placeholder/scaffold for future weather fetch.
// - v0.1 only marks status so the device structure is complete.
(function () {
  "use strict";

  var STATUS_KEY = "hp.weather.status";
  var UPDATED_KEY = "hp.weather.updated";

  function log(s) { print("weather " + String(s || "")); }

  function pad2(n) { n = Number(n); return n < 10 ? "0" + n : String(n); }

  function nowIsoLite() {
    var d = new Date();
    return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()) + "T" +
      pad2(d.getHours()) + ":" + pad2(d.getMinutes()) + ":" + pad2(d.getSeconds());
  }

  function kvSet(key, value, cb) {
    Shelly.call("KVS.Set", { key: key, value: String(value) }, function (res, err) {
      if (err) log("KVS.Set failed " + key + " " + JSON.stringify(err));
      if (cb) cb(!err);
    });
  }

  kvSet(STATUS_KEY, "placeholder", function () {
    kvSet(UPDATED_KEY, nowIsoLite(), function () {
      log("placeholder ok");
    });
  });
})();
