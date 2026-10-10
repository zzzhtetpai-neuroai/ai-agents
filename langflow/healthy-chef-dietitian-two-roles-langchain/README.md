# Healthy Chef: Chef and Dietitian (LangChain)

Generates a recipe, then makes it healthier, using two separate LLM calls with opposite goals.

## How it works
1. **Chef role:** takes a recipe idea or ingredients and writes a creative, tasty recipe
2. **Dietitian role:** reviews the chef's recipe and rewrites it to be healthier, with health comments

The chef's output becomes the dietitian's input. This is called chaining.

## File

### `healthy_chef_adversarial.py`
- Two PromptTemplates, one per role, each with a strict output format
- One model called twice in sequence
- Prints both the original and the healthier version for comparison

## Key concepts
- Adversarial roles: one creates, one critiques
- Why separate calls give each role full focus (vs one combined prompt)
- Prompt templates with placeholders
- Chaining LLM calls

## Run

```bash
python healthy_chef_adversarial.py
```

Try inputs like "chocolate cake" or "chicken, rice, broccoli". Stop with Ctrl+C.
