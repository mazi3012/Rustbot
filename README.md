# Rustbot

Rustbot is a Rust binary that runs [PyBot](https://github.com/huggingface/pybot) through an embedded CPython (PyO3). The chatbot logic is still Python. No PyBot code has been converted to Rust yet.

## Build and run

Requirements: Rust stable, Python 3.11 with its shared library (`libpython3.11.so`) on the loader path.

```bash
cargo build --release
LD_LIBRARY_PATH=/path/to/python3.11/lib ./target/release/rustbot -p "hi, i'm Sam"
```

`pybot.py` and `bot/` must stay in the crate root, next to `Cargo.toml`.

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
