#!/usr/bin/env python3
"""
Generate training data for fine-tuning Needle 3 on PyBot.

Run this script to create a dataset of (message, tool, arguments) examples
by testing PyBot's modules with various inputs.

Usage:
    python training/generate_training_data.py > training_data.jsonl
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import runtime

# Test messages for each module/tool
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
        "hello",
        "how are you?",
        "what's up?",
        "good morning",
        "hi there",
        "hey",
        "good evening",
        "how's it going?",
        "nice to meet you",
        "what can you do?",
    ],
    "greeting": [
        "hello there",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "howdy",
        "greetings",
        "what's happening",
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
        "remember my name?",
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
        "ta",
        "gracias",
    ],
    "goodbye": [
        "goodbye",
        "bye",
        "see you later",
        "take care",
        "good night",
        "see ya",
        "later",
        "ciao",
        "farewell",
        "until next time",
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

# Additional varied messages for robustness
EXTRA_MESSAGES = [
    "My name is John and I need help",
    "I'm feeling really down today",
    "Can you tell me a story?",
    "What's the meaning of life?",
    "I just got promoted!",
    "My dog died yesterday",
    "I'm getting married next week",
    "How do I fix a leaky faucet?",
    "What should I cook for dinner tonight?",
    "I can't sleep",
    "I had a bad dream",
    "My back hurts",
    "I'm hungry",
    "What's your favorite color?",
    "Do you like music?",
    "I'm learning to code",
    "How do I learn Python?",
    "What's the best programming language?",
    "I want to travel to Japan",
    "Recommend a good book",
]


def get_module_for_message(text, memory=None):
    """
    Run PyBot on a message and return which module handled it.
    """
    if memory is None:
        memory = {}
    
    result = runtime.turn(text, memory)
    module = result.get("module", "unknown")
    reply = result.get("reply", "")
    
    return module, reply


def extract_args_from_message(text, tool_name):
    """
    Extract arguments based on the tool type.
    """
    args = {}
    
    if tool_name == "name_store":
        # Try to extract name from message
        import re
        patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"this is (\w+)",
            r"i'm (\w+)",
            r"name's (\w+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                args["name"] = match.group(1).capitalize()
                break
    
    elif tool_name == "safety":
        args["risk_detected"] = "yes"
        args["situation"] = text
    
    elif tool_name in ["chat", "greeting", "question", "feeling", "thanks", "goodbye", "help_seeking"]:
        args["message_type"] = tool_name
        args["topic"] = text[:50]  # First 50 chars as topic
    
    elif tool_name == "context_recall":
        args["action"] = "recall_context"
    
    return args


def generate_training_examples():
    """
    Generate all training examples.
    """
    examples = []
    memory = {}
    
    # Generate examples for each tool
    for tool_name, messages in TEST_MESSAGES.items():
        for msg in messages:
            module, reply = get_module_for_message(msg, memory)
            
            # Map PyBot module to tool name
            # PyBot has 100+ modules, we simplify to a few categories
            mapped_tool = map_module_to_tool(module, tool_name)
            args = extract_args_from_message(msg, mapped_tool)
            
            example = {
                "messages": [
                    {"role": "user", "content": msg}
                ],
                "tool_call": {
                    "name": mapped_tool,
                    "arguments": args
                },
                "expected_reply": reply,
                "pybot_module": module
            }
            examples.append(example)
    
    # Add extra varied messages
    for msg in EXTRA_MESSAGES:
        module, reply = get_module_for_message(msg, memory)
        mapped_tool = map_module_to_tool(module, "chat")
        args = extract_args_from_message(msg, mapped_tool)
        
        example = {
            "messages": [
                {"role": "user", "content": msg}
            ],
            "tool_call": {
                "name": mapped_tool,
                "arguments": args
            },
            "expected_reply": reply,
            "pybot_module": module
        }
        examples.append(example)
    
    return examples


def map_module_to_tool(module, default_tool):
    """
    Map PyBot's internal modules to simplified tool names.
    """
    # Safety-related modules
    if module and any(x in module for x in ["safety", "urgent", "crisis"]):
        return "safety"
    
    # Name-related modules
    if module and any(x in module for x in ["name", "memory_store"]):
        return "name_store"
    
    # Context recall
    if module and any(x in module for x in ["recall", "context", "remember"]):
        return "context_recall"
    
    # Greeting
    if module and module in ["greeting", "chat"]:
        return "greeting"
    
    # Default to chat
    return default_tool


def main():
    print("Generating training data...", file=sys.stderr)
    
    examples = generate_training_examples()
    
    # Output as JSONL
    for example in examples:
        print(json.dumps(example))
    
    print(f"Generated {len(examples)} examples", file=sys.stderr)


if __name__ == "__main__":
    main()
