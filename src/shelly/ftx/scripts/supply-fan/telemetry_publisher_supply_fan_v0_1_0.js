// telemetry_publisher_supply_fan_v0_1_0
var KEY = "ftx.tel.dev.sup";
var KEY_COOL = "ftx.tel.thermal.cool";
var KEY_HEAT = "ftx.tel.thermal.heat";
var HUB_IP = "192.168.77.30";
var COOL_IP = "192.168.77.13";
var HEAT_IP = "192.168.77.12";
var PERIOD_MS = 60000;
var FORCE_S = 600;
var last = null;
var lastS = 0;
var busy = 0;

function log(m) { print(String(m)); }
function isNum(v) { return typeof v === "number" && v === v; }
function n(v, d) { return isNum(v) ? v : d; }
function i(v) { var x = Number(v); if (x !== x) return 0; return Math.floor(x + 0.5); }
function d1(v) { return isNum(v) ? Math.round(v * 10) / 10 : null; }
function b(v) { return v ? 1 : 0; }
function abs(v) { return v < 0 ? -v : v; }
function comp(st, key) { return st && st[key] ? st[key] : null; }
function num4(o, a, c, d, e) {
  if (o && isNum(o[a])) return o[a];
  if (o && isNum(o[c])) return o[c];
  if (o && isNum(o[d])) return o[d];
  if (o && isNum(o[e])) return o[e];
  return null;
}
function temp(st, id) { return d1(num4(comp(st, "temperature:" + id), "tC", "tc", "value", "temp")); }
function pa(st) { return i(n(num4(comp(st, "input:100"), "xpercent", "pa", "pressure", "value"), 0)); }
function light(st) {
  var l = comp(st, "light:0") || {};
  return { on: b(l.output), pct: i(n(l.brightness, 0)), w: i(n(l.apower, 0)) };
}
function uptime(st) {
  var s = comp(st, "sys") || {};
  return i(n(s.uptime, 0));
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
function payload(st) {
  return {
    v: 1,
    device: "sup",
    uptime_s: uptime(st),
    act: light(st),
    pa: pa(st),
    rpm: 0,
    temp: {
      to_house: temp(st, 100),
      post_vvx: temp(st, 101),
      out: temp(st, 102),
      brine: temp(st, 103),
      brine_post_shunt: temp(st, 104),
      hotwater: temp(st, 105),
      hotwater_post_shunt: temp(st, 106)
    }
  };
}
function diff(a, c, d) {
  if (!isNum(a) && !isNum(c)) return 0;
  if (!isNum(a) || !isNum(c)) return 1;
  return abs(a - c) >= d;
}
function changed(cur) {
  if (!last) return 1;
  if ((cur.uptime_s - lastS) >= FORCE_S) return 1;
  if (diff(cur.pa, last.pa, 10)) return 1;
  if (diff(cur.act.w, last.act.w, 2)) return 1;
  if (diff(cur.act.pct, last.act.pct, 1)) return 1;
  if (cur.act.on !== last.act.on) return 1;
  if (diff(cur.temp.to_house, last.temp.to_house, 0.2)) return 1;
  if (diff(cur.temp.post_vvx, last.temp.post_vvx, 0.2)) return 1;
  if (diff(cur.temp.out, last.temp.out, 0.2)) return 1;
  if (diff(cur.temp.brine, last.temp.brine, 0.2)) return 1;
  if (diff(cur.temp.brine_post_shunt, last.temp.brine_post_shunt, 0.2)) return 1;
  if (diff(cur.temp.hotwater, last.temp.hotwater, 0.2)) return 1;
  if (diff(cur.temp.hotwater_post_shunt, last.temp.hotwater_post_shunt, 0.2)) return 1;
  return 0;
}
function publish(cur) {
  var url = "http://" + HUB_IP + "/rpc/KVS.Set?key=" + KEY + "&value=" + enc(JSON.stringify(cur));
  Shelly.call("HTTP.GET", { url: url, timeout: 5 }, function (res, err) {
    if (err || !res || (res.body && res.body.indexOf("error") >= 0)) {
      log("TEL sup put err");
      return;
    }
    publishThermal(cur);
  });
}
function putRemote(ip, key, value, tag, cb) {
  var url = "http://" + ip + "/rpc/KVS.Set?key=" + key + "&value=" + enc(JSON.stringify(value));
  Shelly.call("HTTP.GET", { url: url, timeout: 5 }, function (res, err) {
    if (err || !res || (res.body && res.body.indexOf("error") >= 0)) log("TEL sup " + tag + " err");
    if (cb) cb();
  });
}
function coolPayload(cur) {
  return {
    v: 1,
    source: "sup",
    to_house: cur.temp.to_house,
    brine: cur.temp.brine,
    brine_post_shunt: cur.temp.brine_post_shunt
  };
}
function heatPayload(cur) {
  return {
    v: 1,
    source: "sup",
    to_house: cur.temp.to_house,
    hotwater: cur.temp.hotwater,
    hotwater_post_shunt: cur.temp.hotwater_post_shunt
  };
}
function publishThermal(cur) {
  putRemote(COOL_IP, KEY_COOL, coolPayload(cur), "cool", function () {
    putRemote(HEAT_IP, KEY_HEAT, heatPayload(cur), "heat", function () {
      last = cur;
      lastS = cur.uptime_s;
      log("TEL sup pa=" + cur.pa + " w=" + cur.act.w);
    });
  });
}
function sample() {
  if (busy) return;
  busy = 1;
  Shelly.call("Shelly.GetStatus", {}, function (st, err) {
    var cur;
    busy = 0;
    if (err || !st) {
      log("TEL sup read err");
      return;
    }
    cur = payload(st);
    if (changed(cur)) publish(cur);
  });
}
Timer.set(3000, false, sample);
Timer.set(PERIOD_MS, true, sample);
