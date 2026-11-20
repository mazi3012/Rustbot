# Training Needle 3 on PyBot

This directory contains scripts to fine-tune Needle 3 on PyBot's routing patterns.

## Overview

**Goal:** Create the smallest, smartest local tool-calling + chat model (~50MB total)

**Method:**
1. Generate training data from PyBot's 100+ modules
2. Fine-tune Needle 3 (121M params) with LoRA
3. Result: Needle 3 that understands PyBot's tool schema

## Files

- `generate_training_data.py` - Extract training examples from PyBot
- `finetune_needle3_kaggle.ipynb` - Jupyter notebook for Kaggle GPU training

## Step-by-Step Guide

### Step 1: Generate Training Data

```bash
cd ~/Rustbot
python training/generate_training_data.py > training/training_data.jsonl
```

This creates ~100+ examples of:
- User message
- Correct tool to call
- Arguments to extract

### Step 2: Upload to Kaggle

1. Go to [Kaggle](https://www.kaggle.com)
2. Create a new Dataset:
   - Click "New Dataset"
   - Upload `training_data.jsonl`
   - Name it "pybot-training"

3. Create a new Notebook:
   - Click "New Notebook"
   - Settings > Accelerator > GPU P100 (FREE)
   - Upload `finetune_needle3_kaggle.ipynb`

4. Add your dataset:
   - File > Add Data > Your Datasets > pybot-training

### Step 3: Run Training

Run all cells in the notebook. Training takes ~1-2 hours on P100 GPU.

### Step 4: Download Fine-tuned Model

After training:
1. Download `needle3-pybot-lora.zip`
2. Extract to `Rustbot/weights/needle3-pybot-lora/`

### Step 5: Integrate into Rustbot

```bash
cd ~/Rustbot
cargo build --release
scripts/package.sh
```

## Expected Results

| Metric | Before Fine-tuning | After Fine-tuning |
|--------|-------------------|-------------------|
| Tool calling accuracy | ~30% | ~80-90% |
| Name extraction | Poor | Good |
| Safety detection | Unreliable | Reliable |
| Model size | 35 MB | 35 MB + 5 MB LoRA |

## Training Data Format

Each training example follows this format:

```json
{
  "messages": [
    {"role": "user", "content": "My name is Alice"}
  ],
  "tool_call": {
    "name": "name_store",
    "arguments": {"name": "Alice"}
  },
  "expected_reply": "Hi Alice — good to meet you. What's on your mind?",
  "pybot_module": "name_taken_back"
}
```

## Tools Defined

| Tool | Description | PyBot Modules |
|------|-------------|---------------|
| `name_store` | Store user's name | name_taken_back, memory_store |
| `safety` | Emergency detection | safety, urgent, crisis |
| `chat` | General conversation | chat, greeting, answers |
| `context_recall` | Recall previous context | recall, recap, memory |
| `question` | Factual questions | lookup, knowledge |
| `feeling` | Emotional support | feeling, support |

## Tips for Better Results

1. **More training data = better accuracy**
   - Add more examples to `TEST_MESSAGES` in `generate_training_data.py`
   - Aim for 1000-5000 examples

2. **Diverse examples**
   - Include slang, typos, different phrasings
   - Test with real user messages

3. **Adjust LoRA rank**
   - Higher rank (r=16) = more capacity, larger adapter
   - Lower rank (r=4) = smaller adapter, less capacity
   - Start with r=8

4. **Multiple epochs**
   - 3-5 epochs usually sufficient
   - Watch for overfitting (loss stops decreasing)

## Cost Estimate

- **Kaggle GPU**: FREE (30 hours/week)
- **Training time**: 1-2 hours
- **Total cost**: $0

## Alternative: Use a Different Model

If Needle 3 doesn't work well, try:

| Model | Size | Pros | Cons |
|-------|------|------|------|
| Qwen 2.5 0.5B | 500M | Better tool calling | Larger |
| Phi-3 Mini | 3.8B | Excellent tool calling | Much larger |
| Llama 3.2 1B | 1B | Good balance | Larger than Needle |

## Troubleshooting

### "CUDA out of memory"
- Reduce batch size: `per_device_train_batch_size=2`
- Use gradient checkpointing

### "Training loss doesn't decrease"
- Lower learning rate: `learning_rate=1e-4`
- More training data needed

### "Tool calling still bad after training"
- Need more diverse training examples
- Try higher LoRA rank: `r=16`
- Consider using a larger model

## Next Steps

After successful fine-tuning:
1. Integrate into Rustbot binary
2. Test with real conversations
3. Iterate with more training data
4. Deploy to edge devices!
