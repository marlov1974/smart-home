// state main 1.8.0-device-telemetry
function readInput(ctx, cb) {
  readDeviceTelemetry(ctx, cb);
}

function applyRunCalculations(ctx) {
  applySupplyRun(ctx);
  applyExtractRun(ctx);
  applyVvxRun(ctx);
  applyHeatRun(ctx);
  applyCoolRun(ctx);
  applyDampersRun(ctx);
}

function applyPerfCalculations(ctx, hist) {
  calcPowerFeature(ctx);
  calcVvxEfficiencyFeature(ctx, hist || {});
  calcFanAverageFeature(ctx);
}

function runState() {
  var ctx = createStateCtx();

  log("BOT");

  readInput(ctx, function () {
    readVvxEfficiencyHist(function (hist) {
      applyRunCalculations(ctx);
      applyPerfCalculations(ctx, hist || {});
      writeTelemetryCompat(ctx, function () {
        writeStateOutput(ctx, function () {
          writePowerFeature(ctx, function () {
            writeVvxEfficiencyFeature(ctx, function () {
              writeFanAverageFeature(ctx, function () {
                writeStateStatus(ctx, function () {
                  log("DON");
                  selfStop();
                });
              });
            });
          });
        });
      });
    });
  });
}

runState();
