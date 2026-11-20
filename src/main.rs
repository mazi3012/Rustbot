mod needle;

use pyo3::prelude::*;
use pyo3::types::PyList;
use std::env;
use std::path::PathBuf;

/// Folder that holds `pybot.py` and `bot/`.
fn find_home() -> PathBuf {
    if let Some(home) = env::var_os("RUSTBOT_HOME") {
        return PathBuf::from(home);
    }
    if let Some(dir) = env::current_exe().ok().as_deref().and_then(std::path::Path::parent) {
        for candidate in dir.ancestors().take(4) {
            if candidate.join("pybot.py").is_file() {
                return candidate.to_path_buf();
            }
        }
    }
    PathBuf::from(".")
}

fn main() -> PyResult<()> {
    let home = find_home();

    // Use bundled Python if present, otherwise system Python.
    let bundled = home.join("python");
    if bundled.join("lib").join("python3.11").is_dir() {
        env::set_var("PYTHONHOME", &bundled);
    }

    // UTF-8 mode for proper character handling.
    if env::var_os("PYTHONUTF8").is_none() {
        env::set_var("PYTHONUTF8", "1");
    }

    // Load Needle 3 if the weights are present.
    let needle_engine = home.join("weights").join("needle3.cact");
    let needle_opt = if needle_engine.is_file() {
        println!("Loading Needle 3...");
        match needle::NeedleEngine::load(needle_engine.to_str().unwrap_or("weights/needle3.cact")) {
            Ok(e) => {
                println!("Needle 3 loaded");
                Some(e)
            }
            Err(e) => {
                eprintln!("Failed to load Needle 3: {e}; falling back to PyBot only");
                None
            }
        }
    } else {
        None
    };

    let exit_code = Python::with_gil(|py| -> PyResult<i32> {
        let sys = py.import_bound("sys")?;
        let path: Bound<'_, PyList> = sys.getattr("path")?.downcast_into()?;
        path.insert(0, home.to_string_lossy().as_ref())?;

        let pybot = py.import_bound("pybot")?;

        // Get all arguments after program name.
        let args: Vec<String> = env::args().skip(1).collect();

        // Handle interactive mode differently - Needle is for one-shot routing.
        if args.is_empty() || args.contains(&"--help".to_string()) || args.contains(&"-h".to_string()) {
            // Show help through pybot's main
            pybot.call_method1("main", (args,))?.extract()
        } else if args.contains(&"-p".to_string()) || args.contains(&"--prompt".to_string()) {
            // One-shot with prompt: use Needle for routing, then PyBot for reply.
            let prompt_arg = args
                .iter()
                .position(|a| a == "-p" || a == "--prompt")
                .and_then(|i| args.get(i + 1).cloned())
                .unwrap_or_default();

            if let Some(engine) = &needle_opt {
                match engine.route_message(&prompt_arg) {
                    Ok((tool, args_json)) => {
                        println!("Routed to tool: {tool}");
                        println!("Arguments: {args_json}");
                    }
                    Err(e) => {
                        eprintln!("Needle routing failed: {e}");
                    }
                }
            }

            // PyBot handles the reply regardless of routing.
            pybot.call_method1("main", (args,))?.extract()
        } else {
            // Other modes (pipe, etc.) - pass through to PyBot.
            pybot.call_method1("main", (args,))?.extract()
        }
    })?;

    std::process::exit(exit_code);
}
