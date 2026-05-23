function log(msg) {
  print("hello " + String(msg || ""));
}

function run() {
  log("world");
}

run();
