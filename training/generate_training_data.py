#!/usr/bin/env python3
"""
Generate training data for fine-tuning Needle 3 on PyBot.

Each example is labelled with the category its message was written under (the keys of
TEST_MESSAGES). PyBot's reply is recorded as `expected_reply` for reference only; it is not
used to choose the tool, because PyBot module names do not map cleanly onto tools.

Usage:
    python3 training/generate_training_data.py > training/training_data.jsonl
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import runtime  # noqa: E402

TEST_MESSAGES = {
    "name_store": [
        "my name is Alice",
        "I am Bob",
        "call me Charlie",
        "this is David",
        "name's Emma",
        "I'm Frank",
        "people call me Grace",
        "you can call me Henry",
        "my friends call me Ivy",
        "the name's Jack",
    ],
    "safety": [
        "I have a gun to my head",
        "I'm going to kill myself",
        "I want to end it all",
        "I have a knife and I'm going to use it",
        "I took an overdose",
        "I can't breathe",
        "I'm having a heart attack",
        "severe chest pain",
        "I'm bleeding heavily",
        "I swallowed poison",
    ],
    "chat": [
        "how are you?",
        "what's up?",
        "hi there",
        "hey",
        "how's it going?",
        "nice to meet you",
        "what can you do?",
        "I just got promoted!",
        "I can't sleep",
        "I'm hungry",
        "do you like music?",
        "what's your favorite color?",
        "I'm learning to code",
        "I want to travel to Japan",
    ],
    "greeting": [
        "hello",
        "hello there",
        "good morning",
        "good afternoon",
        "good evening",
        "howdy",
        "greetings",
        "yo",
    ],
    "question": [
        "what is the weather?",
        "how do I cook rice?",
        "what's for dinner?",
        "tell me a joke",
        "what time is it?",
        "where is Paris?",
        "how far is the moon?",
        "why is the sky blue?",
        "who is the president?",
        "when is Christmas?",
    ],
    "feeling": [
        "I'm sad",
        "I feel happy",
        "I'm stressed",
        "I'm tired",
        "I feel great",
        "I'm worried",
        "I'm excited",
        "I feel lonely",
        "I'm bored",
        "I feel anxious",
    ],
    "context_recall": [
        "what were we talking about?",
        "what did I say earlier?",
        "what did you say before?",
        "go back to what we were discussing",
        "what was I asking about?",
        "remind me what we were saying",
        "what were we on about?",
    ],
    "thanks": [
        "thank you",
        "thanks",
        "thanks a lot",
        "thank you very much",
        "I appreciate it",
        "thanks for your help",
        "many thanks",
        "cheers",
    ],
    "goodbye": [
        "goodbye",
        "bye",
        "see you later",
        "take care",
        "good night",
        "see ya",
        "later",
        "farewell",
    ],
    "help_seeking": [
        "help me",
        "I need help",
        "can you help me?",
        "I have a problem",
        "I don't know what to do",
        "I need advice",
        "what should I do?",
        "I'm stuck",
        "I need assistance",
        "can you assist me?",
    ],
}

NAME_PATTERNS = [
    r"my name is (\w+)",
    r"i am (\w+)",
    r"call me (\w+)",
    r"this is (\w+)",
    r"i'm (\w+)",
    r"name's (\w+)",
]


def extract_args(text, tool_name):
    """Arguments that match the tool schema in training/finetune_needle3_kaggle.ipynb."""
    if tool_name == "name_store":
        for pattern in NAME_PATTERNS:
            match = re.search(pattern, text.lower())
            if match:
                return {"name": match.group(1).capitalize()}
        return {"name": ""}
    if tool_name == "safety":
        return {"situation": text}
    return {"topic": text}


def generate_examples():
    examples = []
    for tool_name, messages in TEST_MESSAGES.items():
        for msg in messages:
            memory = {}
            result = runtime.turn(msg, memory)
            examples.append({
                "messages": [{"role": "user", "content": msg}],
                "tool_call": {"name": tool_name, "arguments": extract_args(msg, tool_name)},
                "expected_reply": result.get("reply", ""),
                "pybot_module": result.get("module"),
            })
    return examples


def main():
    examples = generate_examples()
    for example in examples:
        print(json.dumps(example))
    print("Generated", len(examples), "examples", file=sys.stderr)


if __name__ == "__main__":
    main()
