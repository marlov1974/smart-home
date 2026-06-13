// common script 1.1.0-fixed-id-self-stop
function log(s) {
  print(SCRIPT_NAME + " " + String(s || ""));
}

function selfStop() {
  Shelly.call("Script.Stop", { id: SCRIPT_ID }, function () {});
}
