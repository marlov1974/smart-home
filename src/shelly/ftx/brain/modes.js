// brain modes 2.1.0
var MODE_STD = "STD";
var MODE_BST = "BST";
var MODE_FIRE = "FIRE";
var MODE_MAN = "MAN";

function normalizeMode(mode) {
  if (mode !== MODE_STD && mode !== MODE_BST && mode !== MODE_FIRE && mode !== MODE_MAN) return MODE_STD;
  return mode;
}

function isForcedMode(mode) {
  return mode === MODE_BST || mode === MODE_FIRE;
}
