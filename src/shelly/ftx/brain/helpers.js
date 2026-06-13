// brain helpers 2.0.0
function n(v, d) { var x = Number(v); return (x === x) ? x : d; }
function i(v) { var x = Number(v); if (x !== x) return 0; return Math.floor(x + 0.5); }
function d1(v) { var x = Number(v); if (x !== x) return 0; return Math.round(x * 10) / 10; }
function b(v) { return v ? 1 : 0; }
function abs(x) { return x < 0 ? -x : x; }
function clip(v, lo, hi) { var x = Number(v); if (x !== x) x = 0; if (x < lo) x = lo; if (x > hi) x = hi; return x; }
function clipPct(v) { return i(clip(v, 0, 100)); }
function max2(a, b2) { return a > b2 ? a : b2; }
function min2(a, b2) { return a < b2 ? a : b2; }

function getHourNow() { return (new Date()).getHours(); }

function boolGet(id, cb) {
  Shelly.call("Boolean.GetStatus", { id: id }, function (res, err) {
    if (err || !res) { cb(0); return; }
    cb(b(res.value));
  });
}

function enumGet(id, cb) {
  Shelly.call("Enum.GetStatus", { id: id }, function (res, err) {
    if (err || !res || !res.value) { cb(MODE_STD); return; }
    cb(String(res.value));
  });
}

function numberGet(id, cb) {
  Shelly.call("Number.GetStatus", { id: id }, function (res, err) {
    if (err || !res) { cb(21.0); return; }
    cb(n(res.value, 21.0));
  });
}

function enumSet(id, value, cb) { Shelly.call("Enum.Set", { id: id, value: value }, function () { if (cb) cb(); }); }
function numberSet(id, value, cb) { Shelly.call("Number.Set", { id: id, value: value }, function () { if (cb) cb(); }); }
