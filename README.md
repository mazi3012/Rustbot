# Rustbot

Rustbot is a Rust binary that runs [PyBot](https://github.com/huggingface/pybot) through an embedded CPython (PyO3). The chatbot logic is still Python. No PyBot code has been converted to Rust yet.

## Build and run

Requirements to build: Rust stable and CPython 3.11 (`python3` on PATH).

```bash
cargo build --release
./target/release/rustbot -p "hi, i'm Sam"
```

### Portable folder

`scripts/package.sh` builds a folder that runs on its own, without the build machine's Python install:

```bash
scripts/package.sh            # writes dist/rustbot/ (about 140 MB)
dist/rustbot/rustbot -p "hi, i'm Sam"
```

The folder holds the binary, `pybot.py`, `bot/`, and a copy of the Python 3.11 shared library and standard library under `python/`. It can be moved anywhere. The binary finds `bot/` next to itself, or through `RUSTBOT_HOME` if that is set. It sets UTF-8 mode unless `PYTHONUTF8` is already set.

## Benchmark

`benchmark.py` runs PyBot and Rustbot on the same messages and fails if either run exits non-zero or prints nothing.

Measured on this machine, 5 runs each, `-p "test"`:

| Program | Average wall time |
|---|---|
| PyBot (`python3 -m pybot`) | 4.73 s |
| Rustbot (PyO3) | 4.55 s |

About 1.04x. The startup and reply time are dominated by loading PyBot's Python modules, which Rustbot does not change.

## What would make it faster

Only converting PyBot's modules to Rust changes the timing. Rython (`rypip convert`) overflowed the stack on `bot/`, and Brevi rejects PyBot's dynamic code. Neither has produced a working Rust build yet.
