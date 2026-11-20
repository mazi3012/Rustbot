#!/usr/bin/env bash
# Build a self-contained Rustbot folder that runs without the build machine's Python install.
#
#   scripts/package.sh [OUTPUT_DIR]        default OUTPUT_DIR is dist/rustbot
#
# The Python used is the one `python3` finds on PATH. Supports Python 3.11 or 3.12.
# The folder holds the binary, pybot.py, bot/, and the Python shared library and
# standard library under python/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/rustbot}"

PY_VERSION="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if [[ "$PY_VERSION" != "3.11" ]] && [[ "$PY_VERSION" != "3.12" ]]; then
    echo "error: python3 is $PY_VERSION, but the binary requires 3.11 or 3.12" >&2
    exit 1
fi
echo "Using Python $PY_VERSION"

PY_PREFIX="$(python3 -c 'import sys; print(sys.base_prefix)')"
PY_LIB="$PY_PREFIX/lib"

(cd "$ROOT" && cargo build --release)

rm -rf "$OUT"
mkdir -p "$OUT/python/lib"

cp "$ROOT/target/release/rustbot" "$OUT/"
cp "$ROOT/pybot.py" "$OUT/"
cp -r "$ROOT/bot" "$OUT/bot"

# Shared library the binary needs at run time.
cp -P "$PY_LIB"/libpython${PY_VERSION}.so* "$OUT/python/lib/" 2>/dev/null || \
cp -P "$PY_LIB"/libpython${PY_VERSION}m.so* "$OUT/python/lib/" 2>/dev/null || \
cp -P "$PY_LIB"/x86_64-linux-gnu/libpython${PY_VERSION}.so* "$OUT/python/lib/" 2>/dev/null || \
cp -P "$PY_LIB"/x86_64-linux-gnu/libpython${PY_VERSION}m.so* "$OUT/python/lib/" 2>/dev/null || {
    echo "error: could not find libpython${PY_VERSION}.so" >&2
    exit 1
}

# Standard library. Leave out what the bot never imports: test suites, third-party packages,
# the IDLE and Tk GUIs, and compiled caches.
cp -r "$PY_LIB/python${PY_VERSION}" "$OUT/python/lib/python${PY_VERSION}"
rm -rf "$OUT/python/lib/python${PY_VERSION}/test" \
       "$OUT/python/lib/python${PY_VERSION}/site-packages" \
       "$OUT/python/lib/python${PY_VERSION}/idlelib" \
       "$OUT/python/lib/python${PY_VERSION}/tkinter" \
       "$OUT/python/lib/python${PY_VERSION}/turtledemo"
find "$OUT" -name __pycache__ -type d -prune -exec rm -rf {} +

echo "packaged: $OUT"
du -sh "$OUT"
