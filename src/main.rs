use pyo3::prelude::*;
use std::env;

fn main() -> Result<(), PyErr> {
    Python::with_gil(|py| {
        let sys = py.import_bound("sys")?;
        let path = sys.getattr("path")?;
        let path_list: &Bound<'_, pyo3::types::PyList> = path.downcast()?;

        // Directory that holds pybot.py and bot/. Cargo sets this at compile time to the crate root.
        let manifest_dir = env::var("CARGO_MANIFEST_DIR")
            .unwrap_or_else(|_| env!("CARGO_MANIFEST_DIR").to_string());
        path_list.insert(0, &manifest_dir)?;

        let pybot = py.import_bound("pybot")?;
        let args: Vec<String> = env::args().skip(1).collect();
        let result = pybot.call_method("main", (args,), None)?;
        let exit_code: i32 = result.extract()?;

        std::process::exit(exit_code);
    })
}
