use std::process::Command;
use std::env;
use std::path::PathBuf;

fn main() {
    // Get the Rustbot source directory
    let rustbot_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    
    // Run pybot.py with all arguments
    let output = Command::new("python3")
        .arg(rustbot_dir.join("pybot.py"))
        .args(env::args().skip(1))
        .current_dir(&rustbot_dir)
        .output()
        .expect("Failed to execute PyBot");
    
    // Print stdout and stderr
    print!("{}", String::from_utf8_lossy(&output.stdout));
    eprint!("{}", String::from_utf8_lossy(&output.stderr));
    
    std::process::exit(output.status.code().unwrap_or(1));
}
