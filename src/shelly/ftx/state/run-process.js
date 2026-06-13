// state run-process 1.7.0-no-rpm
var VVX_RUN_W_MIN = 10;
var HEAT_RUN_PCT_MIN = 0;
var HEAT_RUN_DT_MIN_C = 0.5;
var COOL_RUN_PCT_MIN = 0;
var COOL_RUN_DT_MIN_C = 0.5;

function applyVvxRun(ctx) {
  var a = ctx.telAct || {};
  var vvx = a.vvx || {};
  ctx.run.vvx = b(on(vvx) && w(vvx) >= VVX_RUN_W_MIN);
}

function applyHeatRun(ctx) {
  var m = ctx.telM || {};
  var a = ctx.telAct || {};
  var heat = a.heat || {};
  var t = m.t || {};
  ctx.run.heat = b(on(heat) && pct(heat) > HEAT_RUN_PCT_MIN && (sget(t, "to_house", 0) - sget(t, "post_vvx", 0)) >= HEAT_RUN_DT_MIN_C);
}

function applyCoolRun(ctx) {
  var m = ctx.telM || {};
  var a = ctx.telAct || {};
  var cool = a.cool || {};
  var t = m.t || {};
  ctx.run.cool = b(on(cool) && pct(cool) > COOL_RUN_PCT_MIN && (sget(t, "post_vvx", 0) - sget(t, "to_house", 0)) >= COOL_RUN_DT_MIN_C);
}

function applyDampersRun(ctx) {
  var a = ctx.telAct || {};
  var dmp = a.dmp || {};
  ctx.run.dmp = b(on(dmp));
}
