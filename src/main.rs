use pyo3::prelude::*;
use pyo3::types::PyList;
use std::env;
use std::path::{Path, PathBuf};

/// Folder that holds `pybot.py` and `bot/`.
///
/// Order: `RUSTBOT_HOME` if set, then the executable's folder and up to three parents, so the
/// binary works from a packaged folder and from `target/release` in the source tree.
fn find_home() -> PathBuf {
    if let Some(home) = env::var_os("RUSTBOT_HOME") {
        return PathBuf::from(home);
    }
    if let Some(dir) = env::current_exe().ok().as_deref().and_then(Path::parent) {
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

    // A packaged build ships its own Python under <home>/python. Point the interpreter there
    // before it starts, so the machine's Python install is not needed.
    let bundled = home.join("python");
    if bundled.join("lib").join("python3.11").is_dir() {
        // Set before the interpreter starts, which happens on the first with_gil call below.
        env::set_var("PYTHONHOME", &bundled);
    }
    // PyBot writes characters such as the em dash. Without a UTF-8 locale, Python would print
    // them as ASCII and fail, so turn on UTF-8 mode unless the user chose otherwise.
    if env::var_os("PYTHONUTF8").is_none() {
        env::set_var("PYTHONUTF8", "1");
    }

    let exit_code = Python::with_gil(|py| -> PyResult<i32> {
        let sys = py.import_bound("sys")?;
        let path: Bound<'_, PyList> = sys.getattr("path")?.downcast_into()?;
        path.insert(0, home.to_string_lossy().as_ref())?;

        let pybot = py.import_bound("pybot")?;
        let args: Vec<String> = env::args().skip(1).collect();
        pybot.call_method1("main", (args,))?.extract()
    })?;

    std::process::exit(exit_code);
}
