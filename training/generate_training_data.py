#!/usr/bin/env python3
"""
Generate training data for fine-tuning Needle 3 on PyBot.

Each example is labelled with the category its message was written under. PyBot's reply is
recorded as `expected_reply` and its module as `pybot_module`, for reference only. Neither is
used to choose the tool, because PyBot module names do not map cleanly onto tools.

Usage:
    python3 training/generate_training_data.py > training/training_data.jsonl
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import runtime  # noqa: E402

NAMES = [
    "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Ivy", "Jack",
    "Priya", "Omar", "Mei", "Lucas", "Fatima", "Ahmed", "Sofia", "Liam", "Chloe", "Mateo",
    "Aisha", "Kenji", "Olivia", "Noah", "Zara", "Ravi", "Hannah", "Diego", "Maya", "Ethan",
]

NAME_TEMPLATES = [
    "my name is {n}",
    "I am {n}",
    "call me {n}",
    "this is {n}",
    "name's {n}",
    "people call me {n}",
    "you can call me {n}",
    "my friends call me {n}",
]

TEST_MESSAGES = {
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
        "my dad just collapsed and isn't breathing",
        "I cut my wrist deep and it won't stop bleeding",
        "I took a whole bottle of pills",
        "someone is choking and can't speak",
        "I'm standing on the edge of the bridge about to jump",
        "I drank bleach",
        "the smoke is so thick I can't breathe in here",
        "my baby stopped breathing",
        "I have a rope and I'm going to hang myself",
        "I think I'm having a stroke, my face is drooping",
        "I've been stabbed in the stomach",
        "my son ate something poisonous and he's unconscious",
        "I'm going to shoot myself tonight",
        "I can't stop vomiting blood",
        "I'm having a seizure right now",
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
        "I went hiking this morning",
        "I finally finished my book",
        "my cat keeps knocking things off the table",
        "the weather is lovely today",
        "I'm watching a new show tonight",
        "I cooked pasta for dinner",
        "I bought a new bike",
        "what do you think about football?",
        "tell me about yourself",
        "I just moved to a new city",
        "I'm thinking about getting a dog",
        "what's a fun thing to do on a rainy day?",
        "I started going to the gym",
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
        "hi again",
        "morning!",
        "hey there, long time no see",
        "good to see you",
        "hiya",
        "hello friend",
        "evening!",
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
        "how many legs does a spider have?",
        "what's the capital of Canada?",
        "how do I boil an egg?",
        "what's a good recipe for lentil soup?",
        "how long should I boil pasta?",
        "what causes rainbows?",
        "how do I change a flat tire?",
        "what's the best way to learn guitar?",
        "how do I make my sourdough rise better?",
        "what's the difference between a virus and bacteria?",
        "how do plants make food?",
        "what should I pack for a beach trip?",
        "how do I write a cover letter?",
        "what's a healthy breakfast?",
        "how much water should I drink a day?",
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
        "I feel really down today",
        "I'm so frustrated with work",
        "I feel overwhelmed",
        "I'm nervous about my exam",
        "I feel like nobody understands me",
        "I'm proud of myself today",
        "I feel calm this evening",
        "I'm heartbroken",
        "I'm scared of the dark",
        "I feel grateful for my friends",
        "I'm jealous of my sister",
        "I'm disappointed I didn't get the job",
        "I feel hopeless lately",
        "I'm angry at my landlord",
        "I'm content with how things are",
    ],
    "context_recall": [
        "what were we talking about?",
        "what did I say earlier?",
        "what did you say before?",
        "go back to what we were discussing",
        "what was I asking about?",
        "remind me what we were saying",
        "what were we on about?",
        "what did I tell you yesterday?",
        "do you remember what I asked first?",
        "what was our last topic?",
        "can you recap what we discussed?",
        "where were we before I got distracted?",
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
        "that was really helpful, thanks",
        "thanks, you made my day",
        "I'm grateful for the advice",
        "ta very much",
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
        "I have to go now, bye",
        "talk to you tomorrow",
        "catch you later",
        "signing off for today",
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
        "I'm not sure how to start my essay, can you guide me?",
        "I need help choosing between two jobs",
        "could you help me plan my week?",
        "I'm lost with this form, can you help?",
        "how can I get my landlord to fix the heating?",
    ],
}


def name_examples():
    """Each name in every other template: 30 names x 4 templates = 120 examples, labelled name_store.

    Fewer templates keep name_store from making up most of the data.
    """
    for name in NAMES:
        for template in NAME_TEMPLATES[::2]:
            yield template.format(n=name), name


def build_example(text, tool_name, arguments):
    memory = {}
    result = runtime.turn(text, memory)
    return {
        "messages": [{"role": "user", "content": text}],
        "tool_call": {"name": tool_name, "arguments": arguments},
        "expected_reply": result.get("reply", ""),
        "pybot_module": result.get("module"),
    }


def generate_examples():
    examples = []
    for text, name in name_examples():
        examples.append(build_example(text, "name_store", {"name": name}))
    for tool_name, messages in TEST_MESSAGES.items():
        for msg in messages:
            if tool_name == "safety":
                arguments = {"situation": msg}
            else:
                arguments = {"topic": msg}
            examples.append(build_example(msg, tool_name, arguments))
    return examples


def main():
    examples = generate_examples()
    for example in examples:
        print(json.dumps(example))
    print("Generated", len(examples), "examples", file=sys.stderr)


if __name__ == "__main__":
    main()
