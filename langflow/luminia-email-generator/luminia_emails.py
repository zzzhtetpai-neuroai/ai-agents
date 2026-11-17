# Luminia: generate a personalized email for each customer
# Data prep with pandas (instead of KNIME), email writing with a Langflow flow (called through its API)
# .env needs: LANGFLOW_URL, LANGFLOW_FLOW_ID, LANGFLOW_API_KEY

# --- Imports ---
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

# --- Settings ---
load_dotenv()
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")
FLOW_ID = os.getenv("LANGFLOW_FLOW_ID")
API_KEY = os.getenv("LANGFLOW_API_KEY")

# Stop right away if a setting is missing
if not (FLOW_ID and API_KEY):
    raise RuntimeError("Set LANGFLOW_FLOW_ID and LANGFLOW_API_KEY in .env")

# Pretend "today" (same as the book), used for days since last purchase
TODAY = pd.Timestamp("2026-12-31")

# Only process the first few customers while testing (saves time and money)
LIMIT = 2


# --- Step 1: load the two files ---
# Why: names/ages are in one file, purchases in the other
customers = pd.read_csv("luminia_customers.csv")
transactions = pd.read_excel("luminia_transactions.xlsx")


# --- Step 2: left join on CustomerID ---
# Why: put each customer next to their purchases, and keep customers who bought nothing
joined = customers.merge(transactions, on="CustomerID", how="left")


# --- Step 3: sort purchases oldest to newest ---
# Why: so the last row of each customer is their newest purchase
joined["PurchaseDate"] = pd.to_datetime(joined["PurchaseDate"])
joined = joined.sort_values("PurchaseDate")


# --- Step 4: group by customer (one row each) ---
# Why: one customer = one email
# Total spent = sum, latest item and date = last
summary = joined.groupby("CustomerID", as_index=False).agg(
    TotalSpend=("Amount", "sum"),
    LastProduct=("ProductName", "last"),
    LastPurchaseDate=("PurchaseDate", "last"),
)
# Bring the customer details back in
summary = customers.merge(summary, on="CustomerID", how="left")


# --- Step 5: days since last purchase ---
# Why: the LLM doesn't know today's date and is bad at date math
summary["DaysFromLastPurchase"] = (TODAY - summary["LastPurchaseDate"]).dt.days


# --- Step 6: build one JSON text per customer ---
# Why: labelled data so the LLM knows which number is which
# Only the fields the LLM needs (no IDs, last names or emails)
FIELDS = [
    "FirstName", "Age", "City", "Country", "Gender", "PreferredCategory",
    "DaysFromSubscription", "TotalSpend", "LastProduct", "DaysFromLastPurchase",
]


def to_customer_json(row) -> str:
    data = {}
    for field in FIELDS:
        value = row[field]
        # Empty values (customers with no purchases) become null
        data[field] = None if pd.isna(value) else value
    return json.dumps(data, default=str)


summary["Customer_data"] = summary.apply(to_customer_json, axis=1)


# --- Step 7: call the Langflow flow for one customer ---
# Why: Langflow holds the prompt, guidelines and LLM; Python just sends data to it
def call_langflow(customer_text: str) -> str:
    url = f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}"
    payload = {
        "input_value": customer_text,
        "input_type": "chat",
        "output_type": "chat",
    }
    headers = {"x-api-key": API_KEY}
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()
    # Dig the chat message text out of Langflow's response
    return data["outputs"][0]["outputs"][0]["results"]["message"]["text"]


# --- Step 8: turn the LLM's answer into subject and body ---
# Why: the LLM returns text that looks like JSON; it can add ```json marks or break
def parse_email(text: str) -> tuple[str, str]:
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        email = json.loads(cleaned)
        return email.get("subject", ""), email.get("body", "")
    except json.JSONDecodeError:
        # Edge case: not valid JSON, keep the raw text so nothing is lost
        return "PARSE_ERROR", text


# --- Step 9: loop over customers ---
# Why: one LLM call per customer, like KNIME's Langflow Runner
batch = summary.head(LIMIT).copy()
subjects, bodies = [], []

for _, row in batch.iterrows():
    print(f"Writing email for {row['FirstName']}...")
    reply = call_langflow(row["Customer_data"])
    subject, body = parse_email(reply)
    subjects.append(subject)
    bodies.append(body)

batch["Subject"] = subjects
batch["Body"] = bodies


# --- Step 10: save to Excel ---
# Why: a mail merge tool can send emails from this file
batch.to_excel("luminia_emails_output.xlsx", index=False)
print("Saved luminia_emails_output.xlsx")