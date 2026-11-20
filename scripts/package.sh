#!/usr/bin/env bash
# Build a self-contained Rustbot folder that runs without the build machine's Python install.
#
#   scripts/package.sh [OUTPUT_DIR]        default OUTPUT_DIR is dist/rustbot
#
# The Python used is the one `python3` finds on PATH. It must be CPython 3.11, the version the
# binary is linked against. The folder holds the binary, pybot.py, bot/, and the Python 3.11
# shared library and standard library under python/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/rustbot}"

PY_VERSION="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if [[ "$PY_VERSION" != "3.11" ]]; then
    echo "error: python3 is $PY_VERSION, but the binary is built against 3.11" >&2
    exit 1
fi
PY_PREFIX="$(python3 -c 'import sys; print(sys.base_prefix)')"
PY_LIB="$PY_PREFIX/lib"

(cd "$ROOT" && cargo build --release)

rm -rf "$OUT"
mkdir -p "$OUT/python/lib"

cp "$ROOT/target/release/rustbot" "$OUT/"
cp "$ROOT/pybot.py" "$OUT/"
cp -r "$ROOT/bot" "$OUT/bot"

# Shared library the binary needs at run time.
cp -P "$PY_LIB"/libpython3.11.so* "$OUT/python/lib/"

# Standard library. Leave out what the bot never imports: test suites, third-party packages,
# the IDLE and Tk GUIs, and compiled caches.
cp -r "$PY_LIB/python3.11" "$OUT/python/lib/python3.11"
rm -rf "$OUT/python/lib/python3.11/test" \
       "$OUT/python/lib/python3.11/site-packages" \
       "$OUT/python/lib/python3.11/idlelib" \
       "$OUT/python/lib/python3.11/tkinter" \
       "$OUT/python/lib/python3.11/turtledemo"
find "$OUT" -name __pycache__ -type d -prune -exec rm -rf {} +

echo "packaged: $OUT"
du -sh "$OUT"
