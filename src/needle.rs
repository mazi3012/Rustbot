use needle_infer::v3_engine::V3Engine;
use pyo3::prelude::*;

/// The tools Rustbot exposes to Needle.
/// 
/// NEEDLE 3 LIMITATIONS:
/// Needle 3 is a 121M parameter model with limited tool calling capability.
/// It doesn't reliably follow tool descriptions and may confuse keywords with names.
/// 
/// CURRENT USE CASE:
/// We keep Needle in the codebase for potential future use (e.g., if a fine-tuned
/// version becomes available), but the primary routing is handled by PyBot's
/// internal module system (bot/modules/), which uses PRIORITY-based routing.
/// 
/// For now, Needle can be used for simple information extraction if needed.
pub const TOOLS_JSON: &str = r#"[]"#;

pub struct NeedleEngine {
    engine: V3Engine,
}

impl NeedleEngine {
    pub fn load(path: &str) -> Result<Self, PyErr> {
        let engine = V3Engine::load(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("failed to load Needle 3: {e}")))?;
        Ok(Self { engine })
    }

    pub fn route_message(&self, message: &str) -> Result<(String, String), PyErr> {
        // Needle 3's tool calling is unreliable. For now, we return a default
        // and let PyBot's modules handle routing via their PRIORITY system.
        // This can be enhanced if a fine-tuned model becomes available.
        Ok(("reply".to_string(), "{}".to_string()))
    }
}
