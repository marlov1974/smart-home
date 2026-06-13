// state run 1.2.1
var SUPPLY_RUN_PCT_MIN = 10;
var SUPPLY_RUN_RPM_MIN = 250;
var SUPPLY_RUN_PA_MIN = 5;

var EXTRACT_RUN_PCT_MIN = 10;
var EXTRACT_RUN_RPM_MIN = 250;
var EXTRACT_RUN_PA_MIN = 5;

var VVX_RUN_RPM_MIN = 4;

var HEAT_RUN_PCT_MIN = 0;
var HEAT_RUN_DT_MIN_C = 0.5;

var COOL_RUN_PCT_MIN = 0;
var COOL_RUN_DT_MIN_C = 0.5;

function applySupplyRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var sup = telAct.sup || {};
  var rpm = telM.rpm || {};
  var pa = telM.pa || {};

  ctx.run.sup = b(
    on(sup) &&
    pct(sup) > SUPPLY_RUN_PCT_MIN &&
    sget(rpm, "sup", 0) > SUPPLY_RUN_RPM_MIN &&
    sget(pa, "sup", 0) >= SUPPLY_RUN_PA_MIN
  );
  cb();
}

function applyExtractRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var ext = telAct.ext || {};
  var rpm = telM.rpm || {};
  var pa = telM.pa || {};

  ctx.run.ext = b(
    on(ext) &&
    pct(ext) > EXTRACT_RUN_PCT_MIN &&
    sget(rpm, "ext", 0) > EXTRACT_RUN_RPM_MIN &&
    sget(pa, "ext", 0) >= EXTRACT_RUN_PA_MIN
  );
  cb();
}

function applyVvxRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var vvx = telAct.vvx || {};
  var rpm = telM.rpm || {};

  ctx.run.vvx = b(on(vvx) && sget(rpm, "vvx", 0) > VVX_RUN_RPM_MIN);
  cb();
}

function applyHeatRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var heat = telAct.heat || {};
  var t = telM.t || {};

  ctx.run.heat = b(
    on(heat) &&
    pct(heat) > HEAT_RUN_PCT_MIN &&
    (sget(t, "to_house", 0) - sget(t, "post_vvx", 0)) >= HEAT_RUN_DT_MIN_C
  );
  cb();
}

function applyCoolRun(ctx, cb) {
  var telM = ctx.telM || {};
  var telAct = ctx.telAct || {};
  var cool = telAct.cool || {};
  var t = telM.t || {};

  ctx.run.cool = b(
    on(cool) &&
    pct(cool) > COOL_RUN_PCT_MIN &&
    (sget(t, "post_vvx", 0) - sget(t, "to_house", 0)) >= COOL_RUN_DT_MIN_C
  );
  cb();
}

function applyDampersRun(ctx, cb) {
  var telAct = ctx.telAct || {};
  var dmp = telAct.dmp || {};

  ctx.run.dmp = b(on(dmp));
  cb();
}
