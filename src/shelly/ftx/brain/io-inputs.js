// brain io-inputs 2.8.0-device-telemetry
var KEY_TEL_DEV_SUP = "ftx.tel.dev.sup";
var KEY_TEL_DEV_EXT = "ftx.tel.dev.ext";
var KEY_TEL_DEV_HEAT = "ftx.tel.dev.heat";
var KEY_TEL_DEV_COOL = "ftx.tel.dev.cool";
var KEY_TEL_DEV_DMP = "ftx.tel.dev.dmp";
var KEY_TEL_DEV_VVX = "ftx.tel.dev.vvx";
var KEY_STATE_RUN = "ftx.state.run";

function getObj(o, k) {
  var x = o && o[k];
  return (x && typeof x === "object") ? x : {};
}

function getGroupValue(dev, group, field, def) {
  var a = getObj(dev, group);
  return (typeof a[field] === "number") ? a[field] : def;
}

function getActNumValue(dev, field, def) {
  return getGroupValue(dev, "act", field, def);
}

function getActBoolValue(dev, field, def) {
  var a = getObj(dev, "act");
  if (typeof a[field] === "number") return b(a[field]);
  return b(def);
}

function getRunValue(run, field, def) {
  if (!run || typeof run !== "object") return def;
  return b(run[field]);
}

function getSafeHouseTemp(ext, def) {
  var x = getGroupValue(ext, "temp", "house", null);
  if (x === null || x === 0) return def;
  return x;
}

function getSafeHouseRh(ext, def) {
  var x = getGroupValue(ext, "rh", "house", null);
  if (x === null || x === 0) return def;
  return x;
}

function readDevKey(key, cb) {
  kvsGet(key, function (value) {
    cb((value && typeof value === "object") ? value : {});
  });
}

function applyInputs(ctx, sup, ext, heat, cool, dmp, vvx, stateRun) {
  ctx.inp.t_out_c = getGroupValue(sup, "temp", "out", ctx.cmd.house_temp_c);
  ctx.inp.t_house_c = getSafeHouseTemp(ext, ctx.cmd.house_temp_c);
  ctx.inp.t_to_house_c = getGroupValue(sup, "temp", "to_house", ctx.cmd.house_temp_c);
  ctx.inp.t_post_vvx_c = getGroupValue(sup, "temp", "post_vvx", ctx.cmd.house_temp_c);
  ctx.inp.rh_house_pct = getSafeHouseRh(ext, 50.0);
  ctx.inp.ppm_house = getGroupValue(ext, "ppm", "house", 500.0);

  ctx.inp.dmp_run = getRunValue(stateRun, "dmp", getActBoolValue(dmp, "on", 0));
  ctx.inp.sup_run = getRunValue(stateRun, "sup", getActBoolValue(sup, "on", 0));
  ctx.inp.ext_run = getRunValue(stateRun, "ext", getActBoolValue(ext, "on", 0));
  ctx.inp.sup_pct_actual = getActNumValue(sup, "pct", 0);
  ctx.inp.ext_pct_actual = getActNumValue(ext, "pct", 0);
  ctx.inp.vvx_on_actual = getActBoolValue(vvx, "on", 0);
  ctx.inp.heat_pct_actual = getActNumValue(heat, "pct", 0);
  ctx.inp.cool_pct_actual = getActNumValue(cool, "pct", 0);
}

function readInputs(ctx, cb) {
  readDevKey(KEY_TEL_DEV_SUP, function (sup) {
    readDevKey(KEY_TEL_DEV_EXT, function (ext) {
      readDevKey(KEY_TEL_DEV_HEAT, function (heat) {
        readDevKey(KEY_TEL_DEV_COOL, function (cool) {
          readDevKey(KEY_TEL_DEV_DMP, function (dmp) {
            readDevKey(KEY_TEL_DEV_VVX, function (vvx) {
              kvsGet(KEY_STATE_RUN, function (r) {
                var stateRun = (r && typeof r === "object") ? r : {};
                applyInputs(ctx, sup, ext, heat, cool, dmp, vvx, stateRun);
                cb();
              });
            });
          });
        });
      });
    });
  });
}
