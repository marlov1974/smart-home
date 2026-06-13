// master_dampers_v0_1_0
var PUBLISHER_ID = 3;
var EXECUTOR_ID = 4;
var EXEC_MS = 61000;
var PUBLISHER_MS = 631000;

function log(m) { print(String(m)); }
function startScript(id, tag) {
  Shelly.call("Script.Start", { id: id }, function (res, err) {
    if (err) log("LM dmp sterr " + tag);
  });
}
function restartPublisher() {
  Shelly.call("Script.Stop", { id: PUBLISHER_ID }, function () {
    Timer.set(300, false, function () { startScript(PUBLISHER_ID, "pub"); });
  });
}
function runExecutor() { startScript(EXECUTOR_ID, "exec"); }
Timer.set(7000, false, restartPublisher);
Timer.set(15000, false, runExecutor);
Timer.set(PUBLISHER_MS, true, restartPublisher);
Timer.set(EXEC_MS, true, runExecutor);
log("LM dmp boot");
