# HistoryTravelBuddy: an agent that plans history-focused day trips using 3 tools
# Setup: uv pip install langchain langchain-openai langchain-community google-search-results wikipedia requests python-dotenv
# .env needs: OPENAI_API_KEY=... and SERP_API_KEY=...

# --- Imports ---
import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# @tool turns a normal Python function into a tool the agent can call
from langchain_core.tools import tool
# Prompt with slots for chat history and the agent's thinking steps
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# Ready-made helpers for Google search (SerpApi) and Wikipedia
from langchain_community.utilities import SerpAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun

# Agent builder + runner (moved to langchain_classic in LangChain 1.0+)
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# --- Load API keys ---
load_dotenv()

# --- Model ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# --- Tool helpers ---
# SerpApi client for Google search results
search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))
# Wikipedia tool: searches and reads articles (ready-made, no extra code needed)
wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


# --- Tool 1: web search ---
# The docstring is the tool description, the agent reads it to decide when to use it
@tool
def web_search(query: str) -> str:
    """Search the web for historical attractions and day-trip ideas."""
    return search.run(query)


# --- Tool 2: open a web page ---
# Downloads the page and returns only the first 2000 characters to save tokens
@tool
def fetch_url(url: str) -> str:
    """Load and retrieve data from specified URLs."""
    text = requests.get(url, timeout=15).text
    return text[:2000]


# --- Give the agent its 3 tools ---
tools = [web_search, fetch_url, wiki_tool]

# --- Agent instructions + message slots ---
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are HistoryTravelBuddy, a helpful assistant that can use tools "
            "to answer questions and perform tasks. You act as an agent, and your "
            "main task is to look for top historical attractions in the city that "
            "the user would like to visit. Open the webpages describing them and "
            "compile a one-day itinerary. Check on Wikipedia for historical facts "
            "about these places and enrich the itinerary with one historical "
            "paragraph for each. Add the link to Wikipedia pages for each "
            "interesting fact you talk about.",
        ),
        # Past conversation (optional)
        MessagesPlaceholder("chat_history", optional=True),
        # The user's request
        ("human", "{input}"),
        # Where the agent's tool calls and results go while it works
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# --- Build the agent ---
# Agent = model + tools + instructions
agent = create_tool_calling_agent(llm, tools, prompt)
# Executor runs the loop: think, call tool, read result, repeat until done
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


# --- Terminal chat ---
def chat_loop() -> None:
    try:
        # Keep asking for trip requests until Ctrl+C
        while True:
            user_input = input("User: ")
            result = agent_executor.invoke({"input": user_input})
            print("\nAI:", result["output"], "\n")
    # Exit cleanly on Ctrl+C
    except KeyboardInterrupt:
        print("\nSafe travels!")


# --- Entry point ---
if __name__ == "__main__":
    chat_loop()