# Luminia Email API: a FastAPI service that writes one personalized email per customer profile
# Same job as the Langflow flow, but as our own HTTP API
# Needs: "Luminia Guidelines.pdf" next to this file, OPENAI_API_KEY in .env
#
# Start the server:
#   uvicorn luminia_email_api:app --reload
# Test it (in another terminal):
#   curl -X POST http://localhost:8000/generate-email \
#        -H "Content-Type: application/json" \
#        -d '{"profile": {"name": "Santoshi", "segment": "lights", "recent_purchase_days_ago": 30}}'

# --- Imports ---
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
# FastAPI builds the web API, pydantic checks the incoming data
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# Reads PDF files
from langchain_community.document_loaders import PyPDFLoader

# --- Settings ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GUIDELINES_PATH = os.path.join(BASE_DIR, "Luminia Guidelines.pdf")

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# --- Load the brand guidelines once at startup ---
# Why: same as Langflow's Read File component
loader = PyPDFLoader(GUIDELINES_PATH)
docs = loader.load()
# Join all PDF pages into one text
guidelines_text = "\n\n".join(page.page_content for page in docs)

# --- Prompt: job + rules (system), customer data (human) ---
PROMPT_TEMPLATE = """
Act as a senior copywriter for Luminia.
Your task is to generate a personalized marketing email that includes:
- A short, engaging subject line
- A concise body tailored to the customer profile (under 120 words)
Follow the brand rules strictly and reference the customer data provided.
Just generate the subject and the body as a JSON object.
The names of the keys must be: 'subject' and 'body'.
------------------------------------------------
### CUSTOMER GUIDELINES
{guidelines}
------------------------------------------------
""".strip()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", PROMPT_TEMPLATE),
        ("human", "{customer_json}"),
    ]
)


# --- Core: one profile in, subject + body out ---
def generate_email_from_profile(profile: Dict[str, Any]) -> Dict[str, str]:
    # Turn the profile into JSON text for the LLM
    customer_json = json.dumps(profile, ensure_ascii=False, indent=2)
    messages = prompt.format_messages(
        guidelines=guidelines_text,
        customer_json=customer_json,
    )
    # Ask the LLM
    text = llm.invoke(messages).content.strip()

    # Remove ```json marks if the LLM added them
    cleaned = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    # Try to read the JSON; if it's broken, keep the raw text so nothing is lost
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"subject": "Luminia special offer", "body": text}

    return {
        "subject": data.get("subject", "Luminia special offer"),
        "body": data.get("body", text),
    }


# --- The shape of incoming requests: {"profile": {...any customer fields...}} ---
class CustomerProfile(BaseModel):
    profile: Dict[str, Any]


# --- The web app ---
app = FastAPI(title="Luminia Email Generator")


# --- The endpoint: POST /generate-email ---
# Why: this is the "takeout window" other programs call
@app.post("/generate-email")
async def generate_email(payload: CustomerProfile) -> Dict[str, str]:
    return generate_email_from_profile(payload.profile)


# --- Quick test without the server: python luminia_email_api.py ---
if __name__ == "__main__":
    sample_profile = {
        "name": "Alex",
        "segment": "loyal_customer",
        "last_purchase_days_ago": 45,
        "preferred_channel": "email",
        "interests": ["smart lighting", "energy savings"],
    }
    print("Sample profile:", json.dumps(sample_profile, indent=2))
    email = generate_email_from_profile(sample_profile)
    print("\nGenerated email:\n", json.dumps(email, indent=2, ensure_ascii=False))