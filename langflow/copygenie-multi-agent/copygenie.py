# CopyGenie: a supervisor agent coordinating planner, copywriter, and delivery agents
# Setup: uv pip install langchain langchain-openai langchain-community docx2txt python-dotenv composio composio-openai
# .env needs: OPENAI_API_KEY, COMPOSIO_API_KEY, COMPOSIO_USER_ID, COMPOSIO_AUTH_CONFIG_ID
# Put the calendar CSV and Brand Guidelines.docx in this folder

# --- Imports ---
import os
from pathlib import Path
from typing import Any, Dict, List

# Reads .docx files as plain text
import docx2txt
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# @tool turns a function into something an agent can call
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
# Composio gives access to Gmail
from composio import Composio
from composio_openai import OpenAIProvider

# --- Load API keys ---
load_dotenv()

# --- Load the calendar and brand guidelines as text ---
BASE_DIR = Path(__file__).resolve().parent
CALENDAR_FILE = BASE_DIR / "Social_Media_Calendar_2025_2027.csv"
BRAND_FILE = BASE_DIR / "Brand Guidelines.docx"
calendar_text = CALENDAR_FILE.read_text(encoding="utf-8")
brand_text = docx2txt.process(str(BRAND_FILE))

# --- Model shared by all agents ---
OPENAI_MODEL = "gpt-4.1-mini"
base_llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.2)

# --- Composio setup ---
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID")
COMPOSIO_AUTH_CONFIG_ID = os.getenv("COMPOSIO_AUTH_CONFIG_ID")

# Stop right away if any Composio setting is missing
if not all([COMPOSIO_API_KEY, COMPOSIO_USER_ID, COMPOSIO_AUTH_CONFIG_ID]):
    raise RuntimeError("Set COMPOSIO_* variables before running CopyGenie.")

composio_client = Composio(
    api_key=COMPOSIO_API_KEY,
    provider=OpenAIProvider(),
    dangerously_skip_version_check=True,
)

# --- Connect Gmail before starting (opens a login link) ---
print("Authorize CopyGenie for Gmail via Composio:")
connection_request = composio_client.connected_accounts.link(
    user_id=COMPOSIO_USER_ID,
    auth_config_id=COMPOSIO_AUTH_CONFIG_ID,
)
print(connection_request.redirect_url)
print("Waiting for Gmail connection...")
connection_request.wait_for_connection()
print("Gmail connection established.\n")


# --- Planner agent: makes a posting plan from the calendar ---
PLANNER_SYSTEM = """
You are Planner Agent for CopyGenie's social media team.
- Use this calendar to find events and space posts evenly:
##{calendar}##
- Default to 4 posts per channel per month unless the user specifies otherwise.
- Output lines like: 11 September: Post about Zero Emissions Day on LinkedIn.
""".strip()

planner_prompt = ChatPromptTemplate.from_messages(
    [("system", PLANNER_SYSTEM), ("human", "{request}")]
)


# The docstring is the description the supervisor sees
@tool
def planner_agent(request: str) -> str:
    """Generates a dated content plan using the social media calendar."""
    messages = planner_prompt.format_messages(calendar=calendar_text, request=request)
    return base_llm.invoke(messages).content.strip()


# --- Copywriter agent: writes posts following brand guidelines ---
COPYWRITER_SYSTEM = """
You are Copywriter Agent for Sol Vigna Wines.
- Follow these brand guidelines: ##{brand_guidelines}##
- Write ONE post per entry from the planner, referencing date/event/channel.
""".strip()

copywriter_prompt = ChatPromptTemplate.from_messages(
    [("system", COPYWRITER_SYSTEM), ("human", "{plan}")]
)


@tool
def copywriter_agent(plan: str) -> str:
    """Drafts branded posts based on the planner's schedule."""
    messages = copywriter_prompt.format_messages(
        brand_guidelines=brand_text,
        plan=plan,
    )
    return base_llm.invoke(messages).content.strip()


# --- Delivery agent: sends the email through Gmail ---
@tool
def delivery_agent(recipient: str, subject: str, body: str) -> str:
    """Sends finalized posts via Gmail through Composio."""
    # Refuse if any email detail is missing
    if not (recipient and subject and body):
        return "Delivery agent needs recipient, subject, and body."
    result = composio_client.tools.execute(
        slug="gmail_send_email",
        arguments={"to": recipient, "subject": subject, "body": body},
        user_id=COMPOSIO_USER_ID,
        dangerously_skip_version_check=True,
    )
    return f"Composio send result: {result}"


# --- Supervisor: decides which agent to call ---
SUPERVISOR_SYSTEM = """
You are CopyGenie, supervising planner_agent, copywriter_agent, delivery_agent.
- Always call planner_agent to read the calendar when users ask about posts.
- Pass planner output to copywriter_agent for branded posts.
- Call delivery_agent only after posts are approved and you have recipient,
  subject, and body. Keep working until the request is fully satisfied.
""".strip()

# Give the supervisor all 3 agents as tools
tools = [planner_agent, copywriter_agent, delivery_agent]
tool_lookup: Dict[str, Any] = {t.name: t for t in tools}
supervisor_model = base_llm.bind_tools(tools)


# --- Chat loop: supervisor calls tools until it has a final answer ---
def run_interactive_chat() -> None:
    # Conversation memory, starting with the supervisor's rules
    messages: List[BaseMessage] = [SystemMessage(content=SUPERVISOR_SYSTEM)]
    try:
        while True:
            user_input = input("User: ")
            if not user_input.strip():
                continue
            messages.append(HumanMessage(content=user_input))

            # Inner loop: keep going while the supervisor wants to call tools
            while True:
                ai_msg = supervisor_model.invoke(messages)
                messages.append(ai_msg)
                tool_calls = getattr(ai_msg, "tool_calls", None) or []

                # No tool calls means the supervisor is done, so print the answer
                if not tool_calls:
                    print("\nAI:", ai_msg.content, "\n")
                    break

                # Run each requested agent and send its result back to the supervisor
                for tc in tool_calls:
                    tool_fn = tool_lookup[tc["name"]]
                    result = tool_fn.invoke(tc["args"])
                    messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tc["id"],
                            name=tc["name"],
                        )
                    )
    # Exit cleanly on Ctrl+C
    except KeyboardInterrupt:
        print("\nCopyGenie signing off!")


# --- Entry point ---
if __name__ == "__main__":
    run_interactive_chat()