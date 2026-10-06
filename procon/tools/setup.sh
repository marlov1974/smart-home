#!/bin/sh
# P0069. Apple Silicon local tool installation; never accesses a device.
set -eu
cd "$(dirname "$0")/.."
test "$(uname -s)/$(uname -m)" = Darwin/arm64 || {
  echo 'Automatic tool installation supports Apple Silicon macOS only. Set TOOLCHAIN for another host.' >&2
  exit 1
}
name=arm-gnu-toolchain-14.3.rel1-darwin-arm64-arm-none-eabi
mkdir -p .local
if ! test -x ".local/$name/bin/arm-none-eabi-gcc"; then
  curl -fL "https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu/14.3.rel1/binrel/$name.tar.xz" -o ".local/$name.tar.xz"
  echo "30f4d08b219190a37cded6aa796f4549504902c53cfc3c7e044a8490b6eba1f7  .local/$name.tar.xz" | shasum -a 256 -c -
  tar -xf ".local/$name.tar.xz" -C .local
fi
if ! test -x .local/venv/bin/python; then python3 -m venv .local/venv; fi
.local/venv/bin/python -m pip install -r tools/requirements.txt
".local/$name/bin/arm-none-eabi-gcc" --version
.local/venv/bin/python --version
