// state run-air 1.7.0-no-rpm
var SUPPLY_RUN_PCT_MIN = 10;
var SUPPLY_RUN_PA_MIN = 5;
var SUPPLY_RUN_W_MIN = 5;
var EXTRACT_RUN_PCT_MIN = 10;
var EXTRACT_RUN_PA_MIN = 5;
var EXTRACT_RUN_W_MIN = 5;

function applySupplyRun(ctx) {
  var m = ctx.telM || {};
  var a = ctx.telAct || {};
  var sup = a.sup || {};
  var pa = m.pa || {};
  ctx.run.sup = b(on(sup) && pct(sup) > SUPPLY_RUN_PCT_MIN && sget(pa, "sup", 0) >= SUPPLY_RUN_PA_MIN && w(sup) >= SUPPLY_RUN_W_MIN);
}

function applyExtractRun(ctx) {
  var m = ctx.telM || {};
  var a = ctx.telAct || {};
  var ext = a.ext || {};
  var pa = m.pa || {};
  ctx.run.ext = b(on(ext) && pct(ext) > EXTRACT_RUN_PCT_MIN && sget(pa, "ext", 0) >= EXTRACT_RUN_PA_MIN && w(ext) >= EXTRACT_RUN_W_MIN);
}
