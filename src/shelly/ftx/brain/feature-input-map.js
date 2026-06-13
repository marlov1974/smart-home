// brain feature-input-map 2.0.0
function getTelM(ctx, path1, path2, def) {
  var a = ctx.telM && ctx.telM[path1];
  if (!a || typeof a !== "object") return def;
  return n(a[path2], def);
}

function getTelActNum(ctx, dev, field, def) {
  var a = ctx.telAct && ctx.telAct[dev];
  if (!a || typeof a !== "object") return def;
  return n(a[field], def);
}

function getTelActBool(ctx, dev, field, def) {
  var a = ctx.telAct && ctx.telAct[dev];
  if (!a || typeof a !== "object") return def;
  return b(a[field]);
}

function mapInputs(ctx) {
  ctx.inp.t_out_c = getTelM(ctx, "t", "out", ctx.cmd.house_temp_c);
  ctx.inp.t_house_c = getTelM(ctx, "t", "house", ctx.cmd.house_temp_c);
  ctx.inp.t_to_house_c = getTelM(ctx, "t", "to_house", ctx.cmd.house_temp_c);
  ctx.inp.t_post_vvx_c = getTelM(ctx, "t", "post_vvx", ctx.cmd.house_temp_c);
  ctx.inp.rh_house_pct = getTelM(ctx, "rh", "house", 50.0);
  ctx.inp.ppm_house = getTelM(ctx, "ppm", "house", 500.0);

  ctx.inp.dmp_run = getTelActBool(ctx, "dmp", "run", 0);
  ctx.inp.sup_run = getTelActBool(ctx, "sup", "run", 0);
  ctx.inp.ext_run = getTelActBool(ctx, "ext", "run", 0);
  ctx.inp.vvx_on_actual = getTelActBool(ctx, "vvx", "on", 0);
  ctx.inp.heat_pct_actual = getTelActNum(ctx, "heat", "pct", 0);
  ctx.inp.cool_pct_actual = getTelActNum(ctx, "cool", "pct", 0);
}
