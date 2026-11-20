use pyo3::prelude::*;
use std::env;

fn main() -> Result<(), PyErr> {
    Python::with_gil(|py| {
        // Import sys module to modify path
        let sys = py.import_bound("sys")?;
        let path = sys.getattr("path")?;
        let path_list: &Bound<'_, pyo3::types::PyList> = path.downcast()?;
        
        // Add current directory (CARGO_MANIFEST_DIR) to Python path
        let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
        path_list.insert(0, manifest_dir)?;
        
        // Import pybot
        let pybot = py.import_bound("pybot")?;
        
        // Get all args after program name
        let args: Vec<String> = env::args().skip(1).collect();
        
        // Call main with args
        let result = pybot.call_method("main", (args,), None)?;
        
        // Get exit code
        let exit_code: i32 = result.extract()?;
        
        std::process::exit(exit_code);
    })
}
