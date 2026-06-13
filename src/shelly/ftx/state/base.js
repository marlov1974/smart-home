// state base 1.8.0-device-telemetry
var SCRIPT_NAME = "state";
var SCRIPT_ID = 5;

var KEY_TEL_M = "ftx.tel.m";
var KEY_TEL_X = "ftx.tel.x";
var KEY_TEL_ACT = "ftx.tel.act";
var KEY_STATE_RUN = "ftx.state.run";
var KEY_TEL_DEV_SUP = "ftx.tel.dev.sup";
var KEY_TEL_DEV_EXT = "ftx.tel.dev.ext";
var KEY_TEL_DEV_HEAT = "ftx.tel.dev.heat";
var KEY_TEL_DEV_COOL = "ftx.tel.dev.cool";
var KEY_TEL_DEV_DMP = "ftx.tel.dev.dmp";
var KEY_TEL_DEV_VVX = "ftx.tel.dev.vvx";

function createStateCtx() {
  return {
    telDev: { sup: {}, ext: {}, heat: {}, cool: {}, dmp: {}, vvx: {} },
    telM: {},
    telX: {},
    telAct: {},
    run: { sup: 0, ext: 0, vvx: 0, heat: 0, cool: 0, dmp: 0 },
    power_w: 0,
    fan_avg_pct: 0,
    vvx_eff_pct: 0,
    vvx_eff_hist: { r0: 0, r1: 0, r2: 0 }
  };
}
