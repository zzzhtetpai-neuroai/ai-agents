# Langflow Learning Projects

Projects built while learning GenAI app development with Langflow and LangChain. Each project was first built as a visual flow in Langflow, then rebuilt in Python to understand what happens behind the drag and drop components.

## Projects

| Folder | What it covers |
|---|---|
| [`pirate-style-chatbot-with-langchain/`](pirate-style-chatbot-with-langchain/) | System prompts, chat loop, and adding conversation memory |
| [`healthy-chef-dietitian-two-roles-langchain/`](healthy-chef-dietitian-two-roles-langchain/) | Prompt templates and chaining two LLM calls with adversarial roles |
| [`RAG/`](RAG/) | Retrieval augmented generation: chunking, embeddings, vector stores (Chroma, FAISS) |
| [`history-travel-buddy-agent/`](history-travel-buddy-agent/) | A tool-using agent with web search (SerpApi), URL reading, and Wikipedia |
| [`copygenie-multi-agent/`](copygenie-multi-agent/) | Multi-agent system: a supervisor with planner, copywriter, and delivery agents that send emails via Gmail |
| [`luminia-email-generator/`](luminia-email-generator/) | Data pipeline with pandas that calls a Langflow flow through its API, plus a FastAPI version |
| [`hungry-traveler-mcp-agent/`](hungry-traveler-mcp-agent/) | Reusing flows as tools through MCP, Gmail sending, and an MCP client in Python |

Each folder has its own README with screenshots and details.

## Setup

```bash
cd langflow
uv venv --python 3.12
source .venv/bin/activate
uv pip install "langflow==1.12.4" "lfx-bundles[chroma,serpapi,wikipedia,composio]"
uv pip check
langflow run
```

Pinning the Langflow version keeps the extra component bundles from pulling in a different version and breaking things.

For the Python scripts, create a `.env` file in the project folder with the keys that project needs (for example `OPENAI_API_KEY`). Never commit it.

## Stack
Langflow, LangChain, OpenAI, Chroma, FAISS, SerpApi, Composio (Gmail), pandas, FastAPI, MCP

Reference: Grokking AI Applications
