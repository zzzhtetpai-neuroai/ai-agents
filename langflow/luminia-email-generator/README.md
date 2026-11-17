# Luminia: Personalized Emails at Scale

Generates a unique marketing email for every customer by combining a data pipeline with an LLM flow.

The book builds the data part in KNIME. I built it in **Python with pandas** instead, and kept the email writer in **Langflow**, called through its API.

## How it works
1. **Load** customer data (CSV) and purchase history (Excel)
2. **Left join** on CustomerID, keeping customers with no purchases
3. **Sort** purchases by date
4. **Group by** customer: total spend, last product, last purchase date
5. **Calculate** days since the last purchase (the LLM can't do date math reliably)
6. **Package** each customer as JSON with only the fields the LLM needs
7. **Call the Langflow flow** through its API, one customer at a time
8. **Parse** the reply into subject and body, keeping the raw text if the JSON is broken
9. **Save** everything to Excel, ready for mail merge

## Pipeline
```
CSV + Excel → join → sort → group → days → JSON → Langflow API → subject/body → Excel
```

## Langflow flow
Read File (brand guidelines PDF) → Prompt Template → OpenAI (system message), with Chat Input carrying one customer's JSON and Chat Output returning `{"subject": ..., "body": ...}`.

## Key concepts
- Running an LLM in a loop over structured data
- ETL with pandas: join, group by, aggregations
- Calling a Langflow flow from code (URL, Flow ID, API key)
- Asking an LLM for JSON output and handling broken JSON

## Run
```bash
python luminia_emails.py
```
Needs `LANGFLOW_URL`, `LANGFLOW_FLOW_ID`, `LANGFLOW_API_KEY` in a `.env` file, Langflow running, and the Luminia data files in this folder (not included). Set `LIMIT` in the script to choose how many customers to process.

## Reference
Learning source: Grokking AI Applications
