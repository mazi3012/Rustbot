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

    let exit_code = Python::with_gil(|py| -> PyResult<i32> {
        let sys = py.import_bound("sys")?;
        let path: Bound<'_, PyList> = sys.getattr("path")?.downcast_into()?;
        path.insert(0, home.to_string_lossy().as_ref())?;

        let pybot = py.import_bound("pybot")?;

        // Get all arguments after program name.
        let args: Vec<String> = env::args().skip(1).collect();

        // Pass through to PyBot for all modes.
        pybot.call_method1("main", (args,))?.extract()
    })?;

    std::process::exit(exit_code);
}
