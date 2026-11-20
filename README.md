# Rustbot

Rustbot is a Rust binary that embeds CPython to run PyBot's chatbot logic. The binary finds `bot/` next to itself and starts an embedded interpreter. No PyBot code has been converted to Rust yet.

## Quick start

### From source tree

```bash
cargo build --release
./target/release/rustbot -p "hi, i'm Sam"
```

### As a portable folder

```bash
cargo build --release && scripts/package.sh
dist/rustbot/rustbot -p "hi, i'm Sam"
```

The portable folder (about 139 MB) runs anywhere, even on a machine without Python, because it bundles Python 3.11. No `LD_LIBRARY_PATH` or locale configuration is needed.

## Features

- **Portable** - Single folder, no build-machine Python required
- **UTF-8 safe** - Works in any locale without crash on special characters
- **Self-contained** - Binary, `bot/`, `pybot.py`, and Python runtime all bundled
- **Fast startup** - Rust entry point, no interpreter startup overhead
- **Needle 3 ready** - Supports Cactus Compute's Needle 3 model for intelligent tool calling

## Current status

| Component | Status |
|---|---|
| Rust binary (PyO3) | ✅ Works, matches PyBot replies |
| Portable folder | ✅ Tested with clean environment |
| Performance | ~1.04x faster than PyBot |
| PyBot code converted to Rust | ❌ Not yet - requires manual porting |
| Needle 3 integration | ⚠️ Model loads, tool calling limited |

## Needle 3 Integration

Rustbot includes support for [Needle 3](https://huggingface.co/CactusCompute/needle-3), a 121M parameter tool-calling model from Cactus Compute.

### What it does
- Loads the `needle3.cact` model from `weights/` folder
- Provides structured tool calling capability
- Extracts information from messages for PyBot modules

### Current limitations
- Needle 3 is a relatively small model (121M parameters)
- Its tool calling capability is limited and may make mistakes
- The model may confuse keywords with names in tool parameters
- For reliable routing, PyBot's internal module system (`bot/modules/`) is used

### Using Needle 3
1. Download `needle3.cact` and place it in `weights/` folder
2. Build and package: `cargo build --release && scripts/package.sh`
3. Run: `dist/rustbot/rustbot -p "your message"`
4. When Needle 3 loads, you'll see: `Loading Needle 3...` and `Needle 3 loaded`

### Future improvements
- Fine-tuning Needle 3 for PyBot's specific tool schema
- Using Needle only for simple pattern matching (name extraction, keyword detection)
- Combining Needle hints with PyBot's PRIORITY-based routing

## Performance notes

PyBot loads ~640K lines of Python on startup, which dominates timing. Each reply takes ~1.4 s in `bot/knowledge/lookup.py`.

**What's fast:**
- Rust binary startup: ~0.01 s (vs ~3.3 s for Python interpreter startup)
- Piped input: 5 messages in one process, ~4.5 s

**What's slow:**
- First message in a fresh process: ~4.5 s (includes Python load)
- Reply computation: ~1.4 s (pure Python in `lookup.py`)

## Building

Requirements:
- Rust stable (tested with 1.100)
- CPython 3.11 with development headers (`python3-dev` on Debian/Ubuntu)

```bash
cargo build --release
```

## Running

The binary automatically locates `bot/` next to itself. If `python/` exists (a bundled Python), it is used automatically. Otherwise, the system Python on PATH is used.

```bash
./target/release/rustbot -p "your message"
./target/release/rustbot < input.txt
```

To use a different `bot/` location, set `RUSTBOT_HOME`:

```bash
RUSTBOT_HOME=/path/to/bot ./target/release/rustbot -p "message"
```

## Testing

```bash
cargo test
```

## License

Apache-2.0 (same as PyBot). The bundled Python 3.11 is also Apache-2.0.

## Future work

- Port `bot/knowledge/lookup.py` to Rust (~8K lines) for 2x speedup
- Integrate Needle 3 for tool calling (currently Rustbot only responds)
