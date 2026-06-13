// state input-devices 1.8.0-device-telemetry
var K_SUPPLY_FAN = 11.6;
var K_EXTRACT_FAN = 12.1;

function obj(o, k) {
  var x = o && o[k];
  return (x && typeof x === "object") ? x : {};
}

function numField(o, k, d) {
  return (o && typeof o[k] === "number") ? o[k] : d;
}

function actFrom(dev, hasPct) {
  var a = obj(dev, "act");
  var out = { on: b(a.on), w: i(clip(numField(a, "w", 0), 0, 9999)) };
  if (hasPct) out.pct = clipPct(numField(a, "pct", 0));
  return out;
}

function normTempOr(v, d) {
  return d1(clip(n(v, d), -99.9, 99.9));
}

function normHouseTemp(v) {
  var x = Number(v);
  if (x !== x || x === 0) return 20.0;
  return d1(clip(x, -20, 50));
}

function normHouseRh(v) {
  var x = Number(v);
  if (x !== x || x === 0) return 60;
  return i(clip(x, 0, 100));
}

function paToLs(pa, k) {
  if (pa <= 0) return 0;
  return i(k * Math.sqrt(pa));
}

function readDevKey(key, cb) {
  kvsGet(key, function (value) {
    cb((value && typeof value === "object") ? value : {});
  });
}

function composeDeviceTelemetry(ctx) {
  var sup = ctx.telDev.sup || {};
  var ext = ctx.telDev.ext || {};
  var heat = ctx.telDev.heat || {};
  var cool = ctx.telDev.cool || {};
  var dmp = ctx.telDev.dmp || {};
  var vvx = ctx.telDev.vvx || {};
  var st = obj(sup, "temp");
  var et = obj(ext, "temp");
  var erh = obj(ext, "rh");
  var eppm = obj(ext, "ppm");
  var supPa = i(clip(numField(sup, "pa", 0), 0, 999));
  var extPa = i(clip(numField(ext, "pa", 0), 0, 999));

  ctx.telM = {
    t: {
      house: normHouseTemp(numField(et, "house", null)),
      out: normTempOr(numField(st, "out", 0), 0),
      to_house: normTempOr(numField(st, "to_house", 0), 0),
      post_vvx: normTempOr(numField(st, "post_vvx", 0), 0),
      to_outdoor: normTempOr(numField(et, "to_outdoor", 0), 0),
      brine: normTempOr(numField(st, "brine", 0), 0),
      hotwater: normTempOr(numField(st, "hotwater", 0), 0)
    },
    rpm: { sup: 0, ext: 0, vvx: 0 },
    pa: { sup: supPa, ext: extPa },
    ls: {
      sup: i(clip(paToLs(supPa, K_SUPPLY_FAN), 0, 999)),
      ext: i(clip(paToLs(extPa, K_EXTRACT_FAN), 0, 999))
    },
    ppm: { house: i(clip(numField(eppm, "house", 0), 0, 2000)) },
    rh: { house: normHouseRh(numField(erh, "house", null)) }
  };

  ctx.telX = {
    t: {
      brine_post_shunt: normTempOr(numField(st, "brine_post_shunt", 0), 0),
      hotwater_post_shunt: normTempOr(numField(st, "hotwater_post_shunt", 0), 0)
    }
  };

  ctx.telAct = {
    sup: actFrom(sup, true),
    ext: actFrom(ext, true),
    vvx: actFrom(vvx, false),
    heat: actFrom(heat, true),
    cool: actFrom(cool, true),
    dmp: actFrom(dmp, false)
  };
}

function readDeviceTelemetry(ctx, cb) {
  readDevKey(KEY_TEL_DEV_SUP, function (sup) {
    ctx.telDev.sup = sup;
    readDevKey(KEY_TEL_DEV_EXT, function (ext) {
      ctx.telDev.ext = ext;
      readDevKey(KEY_TEL_DEV_HEAT, function (heat) {
        ctx.telDev.heat = heat;
        readDevKey(KEY_TEL_DEV_COOL, function (cool) {
          ctx.telDev.cool = cool;
          readDevKey(KEY_TEL_DEV_DMP, function (dmp) {
            ctx.telDev.dmp = dmp;
            readDevKey(KEY_TEL_DEV_VVX, function (vvx) {
              ctx.telDev.vvx = vvx;
              composeDeviceTelemetry(ctx);
              cb();
            });
          });
        });
      });
    });
  });
}
