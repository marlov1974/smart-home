// === DEVICE: dampers-8813bfdaa0c0 / SCRIPT: boot v0.1.0 ===
// Purpose:
// - Lightweight boot scaffold for lab device.
// - Starts Master after boot.
// - Other scripts are intended to be scheduled/test-run manually at this stage.
(function () {
  "use strict";

  var STATUS_KEY = "hp.boot.status";
  var START_MASTER = true;
  var MASTER_NAME = "master";

  function log(s) { print("boot " + String(s || "")); }

  function kvSet(key, value, cb) {
    Shelly.call("KVS.Set", { key: key, value: String(value) }, function (res, err) {
      if (err) log("KVS.Set failed " + key + " " + JSON.stringify(err));
      if (cb) cb(!err);
    });
  }

  function listScripts(cb) {
    Shelly.call("Script.List", {}, function (res, err) {
      if (err || !res || !res.scripts) { cb([]); return; }
      cb(res.scripts);
    });
  }

  function findScriptId(scripts, name) {
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i] && scripts[i].name === name) return scripts[i].id;
    }
    return null;
  }

  function startByName(name, cb) {
    listScripts(function (scripts) {
      var id = findScriptId(scripts, name);
      if (id === null || id === undefined) {
        log("missing " + name);
        if (cb) cb(false);
        return;
      }
      Shelly.call("Script.Start", { id: id }, function (res, err) {
        if (err) {
          log("start failed " + name + " " + JSON.stringify(err));
          if (cb) cb(false);
          return;
        }
        log("started " + name);
        if (cb) cb(true);
      });
    });
  }

  kvSet(STATUS_KEY, "start", function () {
    if (!START_MASTER) {
      kvSet(STATUS_KEY, "ok", null);
      return;
    }
    startByName(MASTER_NAME, function (ok) {
      kvSet(STATUS_KEY, ok ? "ok" : "master_start_failed", null);
    });
  });
})();
