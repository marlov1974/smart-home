// common kvs 1.0.1
function kvsGet(key, cb) {
  Shelly.call("KVS.Get", { key: String(key || "") }, function (res, err) {
    if (err || !res) {
      cb(null);
      return;
    }
    cb(res.value);
  });
}

function kvsSet(key, value, cb) {
  Shelly.call("KVS.Set", { key: String(key || ""), value: value }, function (res, err) {
    if (err) {
      log("KVS ERR");
      if (cb) cb(0);
      return;
    }
    if (cb) cb(1);
  });
}

function kvsWriteObject(key, obj, cb) {
  if (!obj || typeof obj !== "object") obj = {};
  kvsSet(key, obj, cb);
}
