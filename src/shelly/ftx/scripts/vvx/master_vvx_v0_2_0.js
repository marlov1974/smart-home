// master_vvx_v0_2_0
var PUBLISHER_ID = 1;
var EXECUTOR_ID = 10;
var EXEC_MS = 59000;
var PUBLISHER_MS = 619000;

function log(m) { print(String(m)); }
function startScript(id, tag) {
  Shelly.call("Script.Start", { id: id }, function (res, err) {
    if (err) log("LM vvx sterr " + tag);
  });
}
function restartPublisher() {
  Shelly.call("Script.Stop", { id: PUBLISHER_ID }, function () {
    Timer.set(300, false, function () { startScript(PUBLISHER_ID, "pub"); });
  });
}
function runExecutor() { startScript(EXECUTOR_ID, "exec"); }
Timer.set(8000, false, restartPublisher);
Timer.set(17000, false, runExecutor);
Timer.set(PUBLISHER_MS, true, restartPublisher);
Timer.set(EXEC_MS, true, runExecutor);
log("LM vvx boot");
