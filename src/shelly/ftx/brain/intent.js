// brain intent 2.7.2-supply-primary-failsafe
var FAN_START_SUP_PCT = 15;
var FAN_RAMP_STEP_PCT = 5;
var BST_SUP_PCT = 90;
var BST_EXT_PCT = 90;
var FIRE_SUP_PCT = 75;
var FIRE_EXT_PCT = 25;

function baseOffIntent() {
  return {
    driver_inhibit: 0,
    sup:  { on: 0, pct: 0 },
    ext:  { on: 0, pct: 0 },
    vvx:  { on: 0 },
    heat: { on: 0, pct: 0 },
    cool: { on: 0, pct: 0 },
    dmp:  { on: 0 }
  };
}

function resolveDriverInhibit(ctx, intent) {
  intent.driver_inhibit = b(ctx.cmd.mode === MODE_MAN);
}

function resolveDampersAndFansOn(ctx, intent) {
  intent.dmp.on = 1;
  intent.sup.on = 1;
  intent.ext.on = 1;
}

function rampPct(currentPct, desiredPct) {
  var cur = clipPct(currentPct);
  var des = clipPct(desiredPct);
  if (cur < des - FAN_RAMP_STEP_PCT) return clipPct(cur + FAN_RAMP_STEP_PCT);
  if (cur > des + FAN_RAMP_STEP_PCT) return clipPct(cur - FAN_RAMP_STEP_PCT);
  return des;
}

function resolveFanPct(ctx, intent) {
  var desiredSupPct;
  var supPct;
  var extPct;

  if (!ctx.inp.dmp_run) {
    desiredSupPct = FAN_START_SUP_PCT;
  } else if (ctx.sig.freeze_guard_active) {
    desiredSupPct = FAN_START_SUP_PCT;
  } else {
    desiredSupPct = max2(ctx.sig.std_sup_pct, ctx.sig.thermal_sup_pct || 0);

    if (ctx.cmd.mode === MODE_STD && ctx.sig.cool_candidate_pct > 0) {
      desiredSupPct = min2(desiredSupPct, COOL_MAX_SUPPLY_PCT);
    }

    if (ctx.cmd.mode === MODE_STD && ctx.sig.failsafe_active) {
      desiredSupPct = min2(desiredSupPct, ctx.sig.failsafe_sup_pct || 25);
    }
  }

  if (ctx.cmd.mode === MODE_BST) {
    supPct = BST_SUP_PCT;
    extPct = BST_EXT_PCT;
  } else if (ctx.cmd.mode === MODE_FIRE) {
    supPct = FIRE_SUP_PCT;
    extPct = FIRE_EXT_PCT;
  } else {
    supPct = rampPct(ctx.inp.sup_pct_actual, desiredSupPct);
    extPct = extractPctFromSupplyPct(supPct);
  }

  intent.sup.pct = clipPct(supPct);
  intent.ext.pct = clipPct(extPct);
}

function resolveThermalIntent(ctx, intent) {
  intent.heat.pct = ctx.sig.heat_candidate_pct;
  intent.cool.pct = ctx.sig.cool_candidate_pct;
  intent.heat.on = b(ctx.sig.heat_candidate_pct > 0);
  intent.cool.on = b(ctx.sig.cool_candidate_pct > 0);
}

function resolveVvxIntent(ctx, intent) {
  intent.vvx.on = ctx.sig.vvx_candidate_on;
}

function buildIntent(ctx) {
  var intent = baseOffIntent();

  resolveDriverInhibit(ctx, intent);

  if (!ctx.cmd.enable) {
    ctx.intent = intent;
    return;
  }

  resolveDampersAndFansOn(ctx, intent);
  resolveFanPct(ctx, intent);
  resolveVvxIntent(ctx, intent);
  resolveThermalIntent(ctx, intent);

  ctx.intent = intent;
}
