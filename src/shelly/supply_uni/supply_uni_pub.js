// supply_uni_pub P0016 local telemetry publisher proof.
var SCRIPT_NAME = "supply_uni_pub";
var DAMPERS_RPC_URL = "http://192.168.77.30/rpc";
var KEY_SUPPLY_UNI = "tele.supply_uni";
var TICK_MS = 15000;

var KEY_SUPPLY_DP = "voltmeter:100";
var KEY_SUPPLY_RPM = "input:2";
var KEY_TEMP_POST_VVX = "temperature:100";
var KEY_TEMP_OUTDOOR = "temperature:101";
var KEY_TEMP_TO_OUTDOOR = "temperature:102";

var lastSent = null;
var runningTick = 0;

function log(s) {
  print(SCRIPT_NAME + " " + String(s || ""));
}

function num(v, d) {
  var x = Number(v);
  return x === x ? x : d;
}

function round1(v) {
  return Math.round(num(v, 0) * 10) / 10;
}

function clip(v, lo, hi) {
  var x = num(v, 0);
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}

function intClip(v, lo, hi) {
  return Math.floor(clip(v, lo, hi) + 0.5);
}

function tempClip(v) {
  return round1(clip(v, -99.9, 99.9));
}

function abs(v) {
  return v < 0 ? -v : v;
}

function comp(js, key) {
  return js && js[key] ? js[key] : null;
}

function num4(obj, a, b, c, d) {
  if (obj && typeof obj[a] === "number") return obj[a];
  if (obj && typeof obj[b] === "number") return obj[b];
  if (obj && typeof obj[c] === "number") return obj[c];
  if (obj && typeof obj[d] === "number") return obj[d];
  return null;
}

function tempValue(c) {
  return tempClip(num4(c, "tC", "tc", "value", "temp"));
}

function nowTs() {
  return Math.floor((new Date()).getTime() / 1000);
}

function parseSupplyStatus(js) {
  var vm = comp(js, KEY_SUPPLY_DP);
  var inRpm = comp(js, KEY_SUPPLY_RPM);
  return {
    t: nowTs(),
    supply_pa: intClip(num4(vm, "xvoltage", "value", "pa", "pressure"), 0, 999),
    outdoor: tempValue(comp(js, KEY_TEMP_OUTDOOR)),
    post_vvx: tempValue(comp(js, KEY_TEMP_POST_VVX)),
    to_outdoor: tempValue(comp(js, KEY_TEMP_TO_OUTDOOR)),
    supply_rpm: intClip(num4(inRpm, "xfreq", "value", "rpm", "frequency"), 0, 9999)
  };
}

function changedEnough(cur, prev) {
  if (!prev) return true;
  if (abs(cur.supply_pa - prev.supply_pa) >= 10) return true;
  if (abs(cur.outdoor - prev.outdoor) >= 1.0) return true;
  if (abs(cur.post_vvx - prev.post_vvx) >= 1.0) return true;
  if (abs(cur.to_outdoor - prev.to_outdoor) >= 1.0) return true;
  if (abs(cur.supply_rpm - prev.supply_rpm) >= 100) return true;
  return false;
}

function writeRemoteSnapshot(snapshot, cb) {
  var payload = {
    id: 1,
    method: "KVS.Set",
    params: {
      key: KEY_SUPPLY_UNI,
      value: snapshot
    }
  };

  Shelly.call("HTTP.POST", {
    url: DAMPERS_RPC_URL,
    body: JSON.stringify(payload),
    headers: { "Content-Type": "application/json" },
    timeout: 5
  }, function (res, err) {
    if (err || !res || (res.code && res.code >= 400)) {
      log("PUB ERR");
      cb(false);
      return;
    }
    log("PUB OK pa=" + snapshot.supply_pa + " rpm=" + snapshot.supply_rpm);
    cb(true);
  });
}

function tick() {
  if (runningTick) {
    log("BUSY");
    return;
  }

  runningTick = 1;
  Shelly.call("Shelly.GetStatus", {}, function (status, err) {
    var snapshot;
    if (err || !status) {
      log("STATUS ERR");
      runningTick = 0;
      return;
    }

    snapshot = parseSupplyStatus(status);
    log("READ pa=" + snapshot.supply_pa + " rpm=" + snapshot.supply_rpm);
    if (!changedEnough(snapshot, lastSent)) {
      log("NOCHG");
      runningTick = 0;
      return;
    }

    writeRemoteSnapshot(snapshot, function (ok) {
      if (ok) lastSent = snapshot;
      runningTick = 0;
    });
  });
}

function startPublisher() {
  log("BOT");
  Timer.set(500, false, tick);
  Timer.set(TICK_MS, true, tick);
}

startPublisher();
