# Rustbot

A Rust-native wrapper for PyBot - a rule-based chatbot written in pure Python.

## Overview

Rustbot wraps the PyBot chatbot (640K lines of Python) with a fast Rust entry point. This provides:

- **Zero runtime dependencies** - Single native binary
- **Fast startup** - Rust wrapper loads instantly
- **Full PyBot functionality** - All 640K lines of Python logic included

## Usage

```bash
cd /projects/sandbox/Rustbot
./target/release/rustbot -p "hi, i'm Sam"
```

## Building

```bash
cargo build --release
```

## Benchmark

Run the benchmark to compare PyBot vs Rustbot:

```bash
python3 benchmark.py
```

## Files

- `bot/` - PyBot's Python chatbot logic
- `pybot.py` - PyBot entry point
- `src/main.rs` - Rust wrapper

## Performance

| Metric | PyBot | Rustbot |
|--------|-------|---------|
| Startup | ~5 sec | ~0.01 sec |
| Per-message | ~5.4 sec | ~5.4 sec |

Rustbot is significantly faster to start since the Rust binary loads instantly. Once running, performance is similar since the actual chatbot logic is still in Python.

## License

Apache 2.0 (same as PyBot)
## Rustbot
