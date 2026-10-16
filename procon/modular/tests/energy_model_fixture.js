"use strict";

function identity(sid) {
  return [1, sid, sid, 3, 1, 1,
    sid, 0x1110 + sid, 0x2220 + sid, 0x3330 + sid, 0x4440 + sid, 0x5550 + sid,
    0x60 | sid, 1, 0];
}

// Planning fixtures use exact, distinct DIP identities and a malformed model
// record. Production therefore exercises the safe no-seed path immediately.
function respond(method, args, callback) {
  if (method === "KVS.Get" && args.key && args.key.indexOf("vp.effect.a.") === 0) {
    callback({ value: "not-a-model-record", etag: "fixture" }, 0); return true;
  }
  if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 72) {
    callback({ values: identity(args.sid) }, 0); return true;
  }
  if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 308) {
    callback({ values: [4, 0, 1350, 0xffff, 0xfbbe, 0, 3] }, 0); return true;
  }
  if (method === "MbRtuClient.ReadInputRegisters" && args.addr === 346) {
    callback({ values: [0] }, 0); return true;
  }
  return false;
}

module.exports = { identity, respond };
