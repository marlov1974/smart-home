// brain main 2.2.0-signal
function calculateBrain(ctx) {
  calcTarget(ctx);
  calcVentilation(ctx);
  calcFailsafe(ctx);
  calcThermal(ctx);
  calcVvx(ctx);
  buildIntent(ctx);
}

function runBrain() {
  var ctx = createBrainCtx();

  log("BOT");

  readCommands(ctx, function () {
    readInputs(ctx, function () {
      readWeather(ctx, function () {
        readForcedMode(ctx, function () {
          applyForcedModeTimeout(ctx, function () {
            calculateBrain(ctx);
            writeTargetToHouse(ctx, function () {
              writeIntent(ctx, function () {
                log("DON");
                selfStop();
              });
            });
          });
        });
      });
    });
  });
}

runBrain();
