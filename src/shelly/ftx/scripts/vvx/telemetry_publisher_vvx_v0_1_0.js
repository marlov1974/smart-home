// telemetry_publisher_vvx_v0_1_0
var KEY = "ftx.tel.dev.vvx";
var HUB_IP = "192.168.77.30";
var PERIOD_MS = 60000;
var FORCE_S = 600;
var last = null;
var lastS = 0;
var busy = 0;

function log(m) { print(String(m)); }
function isNum(v) { return typeof v === "number" && v === v; }
function n(v, d) { return isNum(v) ? v : d; }
function i(v) { var x = Number(v); if (x !== x) return 0; return Math.floor(x + 0.5); }
function b(v) { return v ? 1 : 0; }
function abs(v) { return v < 0 ? -v : v; }
function comp(st, key) { return st && st[key] ? st[key] : null; }
function sw0(st) {
  var s = comp(st, "switch:0") || {};
  return { on: b(s.output), w: i(n(s.apower, 0)) };
}
function uptime(st) {
  var s = comp(st, "sys") || {};
  return i(n(s.uptime, 0));
}
function payload(st) {
  return { v: 1, device: "vvx", uptime_s: uptime(st), act: sw0(st), rpm: 0 };
}
function changed(cur) {
  if (!last) return 1;
  if ((cur.uptime_s - lastS) >= FORCE_S) return 1;
  if (cur.act.on !== last.act.on) return 1;
  if (abs(cur.act.w - last.act.w) >= 2) return 1;
  return 0;
}
function publish(cur) {
  var url = "http://" + HUB_IP + "/rpc/KVS.Set?key=" + KEY + "&value=" + enc(JSON.stringify(cur));
  Shelly.call("HTTP.GET", { url: url, timeout: 5 }, function (res, err) {
    if (err || !res || (res.body && res.body.indexOf("error") >= 0)) {
      log("TEL vvx put err");
      return;
    }
    last = cur;
    lastS = cur.uptime_s;
    log("TEL vvx on=" + cur.act.on + " w=" + cur.act.w);
  });
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
function sample() {
  if (busy) return;
  busy = 1;
  Shelly.call("Shelly.GetStatus", {}, function (st, err) {
    var cur;
    busy = 0;
    if (err || !st) {
      log("TEL vvx read err");
      return;
    }
    cur = payload(st);
    if (changed(cur)) publish(cur);
  });
}
Timer.set(3000, false, sample);
Timer.set(PERIOD_MS, true, sample);
