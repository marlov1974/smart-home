// state numbers 1.1.1
function n(v, d) {
  var x = Number(v);
  return (x === x) ? x : d;
}

function i(v) {
  var x = Number(v);
  if (x !== x) return 0;
  return Math.floor(x + 0.5);
}

function d1(v) {
  var x = Number(v);
  if (x !== x) return 0;
  return Math.round(x * 10) / 10;
}

function clip(v, lo, hi) {
  var x = Number(v);
  if (x !== x) x = 0;
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}

function b(v) {
  return v ? 1 : 0;
}

function abs(x) {
  return x < 0 ? -x : x;
}

function sget(o, a, d) {
  if (o && typeof o[a] === "number") return o[a];
  return d;
}

function on(o) {
  return o && o.on ? 1 : 0;
}

function pct(o) {
  return sget(o, "pct", 0);
}

function w(o) {
  return sget(o, "w", 0);
}

function clipPct(v) {
  return i(clip(v, 0, 100));
}
