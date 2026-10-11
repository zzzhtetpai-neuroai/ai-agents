# RAG chatbot over a restaurant menu PDF (LangChain version of the Langflow RAG flow)
# Setup: uv pip install pypdf chromadb langchain-openai langchain-community langchain-text-splitters python-dotenv
# Key goes in a .env file as OPENAI_API_KEY=...
# The menu PDF must be in the same folder as this script

# --- Imports ---
import os
from pathlib import Path

from dotenv import load_dotenv
# Chat model + embedding model
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# Vector database
from langchain_community.vectorstores import Chroma
# Reads PDF files
from langchain_community.document_loaders import PyPDFLoader
# Cuts text into chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

# --- Paths and settings ---
# Folder where this script lives
BASE_DIR = Path(__file__).resolve().parent
# The PDF to load
MENU_PDF = BASE_DIR / "Lu Sule Pizzeria - Info and Menu.pdf"
# Folder where Chroma saves the database
INDEX_DIR = BASE_DIR / "menu"
COLLECTION_NAME = "menu"

# --- Load the API key ---
load_dotenv()


# --- Build or load the vector database ---
def ensure_vectorstore(pdf_path: Path, index_dir: Path) -> Chroma:
    # Embedding model turns text into numbers for similarity search
    embeddings = OpenAIEmbeddings()

    # If the database already exists, just load it (no re-ingestion, no extra cost)
    if index_dir.exists():
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(index_dir),
        )

    # Otherwise: read the PDF
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()

    # Split it into chunks (same settings as the Langflow Split Text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    # Embed the chunks and save them in Chroma
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(index_dir),
    )
    return vectorstore


# --- Prompt that forces answers to come from the menu ---
def build_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["chunks", "message"],
        template=(
            "Answer the user query by using only the provided context.\n"
            "Context:\n{chunks}\n\nUser: {message}"
        ),
    )


# --- Set everything up once ---
VECTORSTORE = ensure_vectorstore(MENU_PDF, INDEX_DIR)
# Retriever returns the 4 most similar chunks for each question
RETRIEVER = VECTORSTORE.as_retriever(search_kwargs={"k": 4})
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
PROMPT = build_prompt()


# --- Retrieve, build prompt, generate ---
def answer_query(question: str) -> str:
    # 1. Find the most relevant chunks
    docs = RETRIEVER.invoke(question)
    # 2. Join their text into one context block
    context = "\n\n".join(doc.page_content for doc in docs)
    # 3. Put context + question into the prompt
    final_prompt = PROMPT.format(chunks=context, message=question)
    # 4. Ask the model
    response = LLM.invoke(final_prompt)
    return response.content


# --- Terminal chat ---
def chat_loop() -> None:
    try:
        # Keep asking questions until Ctrl+C
        while True:
            user_question = input("Your PizzaMate question: ")
            answer = answer_query(user_question)
            print("\nAI:", answer, "\n")
    # Exit cleanly on Ctrl+C
    except KeyboardInterrupt:
        print("\nEnjoy your slice!")


# --- Entry point ---
if __name__ == "__main__":
    chat_loop()