# Langflow Learning Projects

Projects built while learning GenAI app development with Langflow and LangChain.
Each folder rebuilds a Langflow visual flow in Python code using LangChain, to understand what happens behind the drag and drop components.

## Projects

| Folder | What it covers |
|---|---|
| `pirate-style-chatbot-with-langchain/` | System prompts, chat loop, and adding conversation memory |
| `healthy-chef-dietitian-two-roles-langchain/` | Prompt templates and chaining two LLM calls with adversarial roles |

## Setup

```bash
cd langflow
uv venv --python 3.12
source .venv/bin/activate
uv pip install langflow langchain-openai langchain-core python-dotenv
```

Create a `.env` file with your key (never commit it):

```
OPENAI_API_KEY=your-key-here
```

## Running Langflow

```bash
langflow run
```

Then open http://localhost:7860

## Stack
Python, Langflow, LangChain, OpenAI API, WSL Ubuntu
