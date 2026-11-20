use needle_infer::v3_engine::V3Engine;
use pyo3::prelude::*;

/// The tools Rustbot exposes to Needle.
pub const TOOLS_JSON: &str = r#"[
    {"name":"reply","description":"General conversation and answering questions","parameters":{"type":"object","properties":{"topic":{"type":"string"}},"required":["topic"]}},
    {"name":"safety","description":"Emergency guidance for self-harm, poisoning, or medical crisis","parameters":{"type":"object","properties":{"situation":{"type":"string"}},"required":["situation"]}},
    {"name":"remember_name","description":"Store the user's name for future turns","parameters":{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}},
    {"name":"recall_name","description":"Recall the user's name from memory","parameters":{"type":"object","properties":{}}}
]"#;

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
        let result = self
            .engine
            .run_json(message, TOOLS_JSON)
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Needle routing failed"))?;

        if result.is_empty() {
            return Ok(("reply".to_string(), "{\"topic\":\"general\"}".to_string()));
        }

        let call: serde_json::Value = serde_json::from_str(&result)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("failed to parse Needle output: {e}")))?;

        let tool_name = call
            .get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("reply")
            .to_string();

        let arguments = call
            .get("arguments")
            .and_then(|v| Some(v.to_string()))
            .unwrap_or("{}".to_string());

        Ok((tool_name, arguments))
    }
}
