// state feature-run-supply 1.2.0
var SUPPLY_RUN_PCT_MIN = 10;
var SUPPLY_RUN_RPM_MIN = 250;
var SUPPLY_RUN_PA_MIN = 5;

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
