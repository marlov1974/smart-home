// common number 1.0.0
function numberSet(id, value, cb) {
  Shelly.call("Number.Set", { id: id, value: value }, function () {
    if (cb) cb();
  });
}
