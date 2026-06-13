// brain output 2.12.0-vvx-local-thermal-intent
var KEY_INTENT_DEV_SUP = "ftx.intent.dev.sup";
var KEY_INTENT_DEV_EXT = "ftx.intent.dev.ext";
var KEY_INTENT_DEV_HEAT = "ftx.intent.dev.heat";
var KEY_INTENT_DEV_COOL = "ftx.intent.dev.cool";
var KEY_INTENT_DEV_DMP = "ftx.intent.dev.dmp";
var KEY_INTENT_DEV_VVX = "ftx.intent.dev.vvx";
var VM_TARGET_TO_HOUSE_ID = 204;
var IP_SUPPLY_FAN = "192.168.77.10";
var IP_EXTRACT_FAN = "192.168.77.11";
var IP_HEAT = "192.168.77.12";
var IP_COOL = "192.168.77.13";
var IP_VVX = "192.168.77.40";

function nowTs() {
  return Math.floor((new Date()).getTime() / 1000);
}

function enc(s) {
  var out = "";
  var i2;
  var c;
  var h;
  for (i2 = 0; i2 < s.length; i2++) {
    c = s.charAt(i2);
    if ((c >= "A" && c <= "Z") || (c >= "a" && c <= "z") || (c >= "0" && c <= "9") || c === "-" || c === "_" || c === "." || c === "~") {
      out += c;
    } else {
      h = c.charCodeAt(0).toString(16).toUpperCase();
      if (h.length < 2) h = "0" + h;
      out += "%" + h;
    }
  }
  return out;
}

function buildDeviceIntent(ctx, device, act, ts) {
  var intent = ctx.intent || baseOffIntent();
  var mode = ctx.cmd && ctx.cmd.mode ? String(ctx.cmd.mode) : MODE_STD;
  var out = {
    v: 1,
    source: "brain",
    ts: ts,
    device: device,
    mode: mode,
    driver_inhibit: intent.driver_inhibit ? 1 : 0,
    act: act || {}
  };
  if (device === "heat" || device === "cool" || device === "vvx") {
    out.target_to_house_c = d1(ctx.sig ? ctx.sig.target_to_house_c : 0);
    out.act.target_to_house_c = out.target_to_house_c;
  }
  if (device === "vvx") {
    out.temp = {
      out_c: d1(ctx.inp ? ctx.inp.t_out_c : 0),
      house_c: d1(ctx.inp ? ctx.inp.t_house_c : 0)
    };
  }
  return out;
}

function remoteKvsSet(ip, key, value, cb) {
  var url = "http://" + ip + "/rpc/KVS.Set?key=" + key + "&value=" + enc(JSON.stringify(value));
  Shelly.call("HTTP.GET", { url: url, timeout: 5 }, function (res, err) {
    if (err || !res || (res.body && res.body.indexOf("error") >= 0)) log("RKV ERR " + key);
    if (cb) cb();
  });
}

function writeDeviceIntents(ctx, cb) {
  var intent = ctx.intent || baseOffIntent();
  var ts = nowTs();
  remoteKvsSet(IP_SUPPLY_FAN, KEY_INTENT_DEV_SUP, buildDeviceIntent(ctx, "sup", intent.sup, ts), function () {
    remoteKvsSet(IP_EXTRACT_FAN, KEY_INTENT_DEV_EXT, buildDeviceIntent(ctx, "ext", intent.ext, ts), function () {
      remoteKvsSet(IP_HEAT, KEY_INTENT_DEV_HEAT, buildDeviceIntent(ctx, "heat", intent.heat, ts), function () {
        remoteKvsSet(IP_COOL, KEY_INTENT_DEV_COOL, buildDeviceIntent(ctx, "cool", intent.cool, ts), function () {
          kvsSet(KEY_INTENT_DEV_DMP, buildDeviceIntent(ctx, "dmp", intent.dmp, ts), function () {
            remoteKvsSet(IP_VVX, KEY_INTENT_DEV_VVX, buildDeviceIntent(ctx, "vvx", intent.vvx, ts), cb);
          });
        });
      });
    });
  });
}

function writeIntent(ctx, cb) {
  writeDeviceIntents(ctx, cb);
}

function writeTargetToHouse(ctx, cb) {
  var value = d1(ctx.sig ? ctx.sig.target_to_house_c : 0);
  numberSet(VM_TARGET_TO_HOUSE_ID, value, cb);
}
