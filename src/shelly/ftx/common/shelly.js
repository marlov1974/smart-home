// common shelly 1.0.3-no-dup-helpers
function httpGetStatus(ip, cb) {
  var done = false;
  var timer = null;

  function finish(js) {
    if (done) return;
    done = true;
    if (timer) {
      Timer.clear(timer);
      timer = null;
    }
    cb(js);
  }

  timer = Timer.set(4500, false, function () {
    timer = null;
    finish(null);
  });

  Shelly.call("HTTP.GET", { url: "http://" + ip + "/rpc/Shelly.GetStatus", timeout: 3 }, function (res, err) {
    if (err || !res || !res.body) {
      finish(null);
      return;
    }
    try {
      finish(JSON.parse(res.body));
    } catch (e) {
      finish(null);
    }
  });
}

function comp(js, key) {
  return (js && js[key]) ? js[key] : null;
}

function num1(obj, a) {
  return (obj && typeof obj[a] === "number") ? obj[a] : null;
}

function num2(obj, a, b2) {
  if (obj && typeof obj[a] === "number") return obj[a];
  if (obj && typeof obj[b2] === "number") return obj[b2];
  return null;
}

function num3(obj, a, b2, c) {
  if (obj && typeof obj[a] === "number") return obj[a];
  if (obj && typeof obj[b2] === "number") return obj[b2];
  if (obj && typeof obj[c] === "number") return obj[c];
  return null;
}

function num4(obj, a, b2, c, d) {
  if (obj && typeof obj[a] === "number") return obj[a];
  if (obj && typeof obj[b2] === "number") return obj[b2];
  if (obj && typeof obj[c] === "number") return obj[c];
  if (obj && typeof obj[d] === "number") return obj[d];
  return null;
}

function bool2(obj, a, b2) {
  if (obj && typeof obj[a] === "boolean") return obj[a];
  if (obj && typeof obj[b2] === "boolean") return obj[b2];
  return false;
}

function tempValue(c) {
  return n(num4(c, "tC", "tc", "value", "temp"), 0);
}

function parseLight0(js) {
  var light = comp(js, "light:0");
  return {
    on: b(bool2(light, "output", "ison")),
    pct: clipPct(num2(light, "brightness", "brightness_set")),
    w: i(n(num1(light, "apower"), 0))
  };
}

function parseSwitch0(js) {
  var sw = comp(js, "switch:0");
  return {
    on: b(bool2(sw, "output", "state")),
    w: i(n(num1(sw, "apower"), 0))
  };
}
