// state components 1.1.3
function numberSet(id, value, cb) {
  Shelly.call("Number.Set", { id: id, value: value }, function () {
    if (cb) cb();
  });
}
