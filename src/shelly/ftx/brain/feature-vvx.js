// brain feature-vvx 2.5.0-local-vvx-allow
function calcVvx(ctx) {
  ctx.sig.vvx_candidate_on = ctx.cmd && ctx.cmd.enable ? 1 : 0;
  ctx.sig.vvx_reason = ctx.sig.vvx_candidate_on ? "ALLOW" : "OFF";
}
