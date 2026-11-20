#!/usr/bin/env python3
"""
Convert training/training_data.jsonl into the format `cactus finetune` reads.

Input rows:  {"messages": [...], "tool_call": {"name", "arguments"}, ...}
Output rows: {"query", "tools", "answers", "reasoning"}  (one JSON object per line)

Every row carries the same tool catalogue, so the model learns to choose among all tools.
Small talk, feelings and help requests get "answers": [] because PyBot answers them without a tool.

Usage:
    python3 training/convert_to_cactus.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(HERE, "training_data.jsonl")
OUTPUT = os.path.join(HERE, "cactus_data.jsonl")

TOOLS = [
    {
        "name": "name_store",
        "description": "Remember the name the user gives themselves, e.g. 'my name is Alice'.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "The name exactly as written."}},
            "required": ["name"],
        },
    },
    {
        "name": "safety",
        "description": "Emergency: the user describes a life-threatening situation happening now.",
        "parameters": {
            "type": "object",
            "properties": {"situation": {"type": "string", "description": "What is happening."}},
            "required": ["situation"],
        },
    },
    {
        "name": "context_recall",
        "description": "The user asks what was said earlier in this conversation.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "answer_question",
        "description": "The user asks a factual or how-to question.",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "The question asked."}},
            "required": ["question"],
        },
    },
]

TOOL_FOR = {
    "name_store": "name_store",
    "safety": "safety",
    "context_recall": "context_recall",
    "question": "answer_question",
}

NO_TOOL_REASON = "small talk, feeling or request for help; no tool needed"


def convert(row):
    query = row["messages"][0]["content"]
    label = row["tool_call"]["name"]
    tool = TOOL_FOR.get(label)
    if tool is None:
        return {"query": query, "tools": TOOLS, "answers": [], "reasoning": NO_TOOL_REASON}

    args = row["tool_call"]["arguments"]
    if tool == "name_store":
        arguments = {"name": args["name"]}
        reasoning = "'%s' -> name" % args["name"]
    elif tool == "safety":
        arguments = {"situation": query}
        reasoning = "whole message -> situation"
    elif tool == "answer_question":
        arguments = {"question": query}
        reasoning = "whole message -> question"
    else:
        arguments = {}
        reasoning = "asks about earlier chat; no arguments"
    return {
        "query": query,
        "tools": TOOLS,
        "answers": [{"name": tool, "arguments": arguments}],
        "reasoning": reasoning,
    }


def main():
    with open(INPUT, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    converted = [convert(row) for row in rows]
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        for item in converted:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    with_tool = sum(1 for item in converted if item["answers"])
    print("wrote", len(converted), "examples to", OUTPUT)
    print("with a tool call:", with_tool, "| answers []:", len(converted) - with_tool)


if __name__ == "__main__":
    main()
