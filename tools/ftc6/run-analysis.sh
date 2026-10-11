#!/bin/sh
# P0082. Only the pinned operator-supplied image; all full output stays in LOCAL_OUT.
set -eu
: "${GHIDRA_HOME:?Set GHIDRA_HOME to installed Ghidra 12.1.4}"
: "${JAVA_HOME:?Set JAVA_HOME to JDK 21}"
: "${FTC6_MOT:?Set FTC6_MOT to local original}"
: "${LOCAL_OUT:?Set LOCAL_OUT outside any public repository}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()=="e94f9d9369b5efb9d2af66209fb431fde6ed0a1690b9ce0960adbf5cdb53b0c3", "Unsupported image: review seeds first"' "$FTC6_MOT"
mkdir -p "$LOCAL_OUT/projects" "$LOCAL_OUT/evidence"
python3 "$SCRIPT_DIR/inspect_image.py" "$FTC6_MOT" --report "$LOCAL_OUT/image-validation.json"
"$GHIDRA_HOME/support/analyzeHeadless" "$LOCAL_OUT/projects" ftc6 -import "$FTC6_MOT" -loader MotorolaHexLoader -processor m16c:LE:16:default -noanalysis -scriptPath "$SCRIPT_DIR" -postScript P82Audit.java "$LOCAL_OUT/evidence" -log "$LOCAL_OUT/ghidra.log"
