# PizzaMate: RAG Chatbot (LangChain)

A chatbot that answers questions about a restaurant using only its menu PDF, built with Retrieval-Augmented Generation.

## How it works
1. **Ingest:** load the PDF, split it into chunks (400 chars, 150 overlap), embed them, store in Chroma
2. **Retrieve:** for each question, find the 4 most similar chunks
3. **Generate:** send the chunks + question to the LLM, which answers using only that context

The Chroma database is saved to disk, so the PDF is only processed once.

## File
### `pizzamate_rag.py`
- PyPDFLoader to read the document
- RecursiveCharacterTextSplitter for chunking
- OpenAI embeddings + Chroma vector store
- Retriever (top k = 4) + prompt that restricts answers to the context

## Key concepts
- Chunk size and overlap
- Embeddings and similarity search
- Grounding answers in retrieved context to reduce hallucination

## Run
```bash
python pizzamate_rag.py
```
Place a PDF named `Lu Sule Pizzeria - Info and Menu.pdf` in this folder first (not included in the repo).
Delete the `menu/` folder to rebuild the database after changing the PDF.
