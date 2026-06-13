// brain io-commands 2.3.0-local-dampers-command-source
var CMD_ENABLE_ID = 200;
var CMD_NIGHT_SETBACK_ID = 201;
var CMD_MODE_ID = 200;
var CMD_HOUSE_TEMP_ID = 200;

function localBoolGet(id, fallback, cb) {
  Shelly.call("Boolean.GetStatus", { id: id }, function (res, err) {
    if (err || !res || typeof res.value === "undefined") { cb(fallback); return; }
    cb(b(res.value));
  });
}

function localEnumGet(id, cb) {
  Shelly.call("Enum.GetStatus", { id: id }, function (res, err) {
    if (err || !res || !res.value) { cb(MODE_STD); return; }
    cb(String(res.value));
  });
}

function localNumberGet(id, cb) {
  Shelly.call("Number.GetStatus", { id: id }, function (res, err) {
    if (err || !res) { cb(21.0); return; }
    cb(n(res.value, 21.0));
  });
}

function readCommands(ctx, cb) {
  ctx.cmd.enable = 1;
  ctx.cmd.night_setback = 0;
  ctx.cmd.mode = MODE_STD;
  ctx.cmd.house_temp_c = 21.0;

  localBoolGet(CMD_ENABLE_ID, 1, function (vEnable) {
    ctx.cmd.enable = vEnable;
    localBoolGet(CMD_NIGHT_SETBACK_ID, 0, function (vNight) {
      ctx.cmd.night_setback = vNight;
      localEnumGet(CMD_MODE_ID, function (vMode) {
        ctx.cmd.mode = normalizeMode(vMode);
        localNumberGet(CMD_HOUSE_TEMP_ID, function (vTemp) {
          ctx.cmd.house_temp_c = n(vTemp, 21.0);
          cb();
        });
      });
    });
  });
}
