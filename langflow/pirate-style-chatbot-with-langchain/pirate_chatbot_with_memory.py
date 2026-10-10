# Chat loop with memory (history injected into the prompt each turn)
# Setup: uv pip install langchain-openai langchain-core python-dotenv
# Key goes in a .env file as OPENAI_API_KEY=...

# --- Imports ---
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# PromptTemplate = a prompt with blanks to fill in
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# --- Load the API key ---
load_dotenv()

# Stop right away if the key is missing
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Set OPENAI_API_KEY before running this script.")

# --- Model and behavior rules ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
system_msg = SystemMessage(content="Always reply in Pirate English.")

# --- Prompt template ---
# Two blanks: past conversation goes first, then the new user message
prompt = PromptTemplate(
    input_variables=["message", "history"],
    template="{history}\nUser: {message}\nAI: ",
)


# --- Chat loop with memory ---
def chat_loop() -> None:
    # The memory: a list that stores every past line of the conversation
    history_lines: list[str] = []

    try:
        while True:
            # Join past lines into one text block
            history_block = "\n".join(history_lines)

            # Get the new message from the user
            user_input = input("User: ")

            # Fill the template blanks with history + new message
            rendered_prompt = prompt.format(message=user_input, history=history_block)

            # Send system rule + the filled prompt to the model
            response = llm.invoke(
                [system_msg, HumanMessage(content=rendered_prompt)]
            )
            print("AI:", response.content)

            # Save this turn into memory so the next turn can see it
            history_lines.extend(
                [f"User: {user_input}", f"AI: {response.content}"]
            )

    # Exit cleanly on Ctrl+C
    except KeyboardInterrupt:
        print("\nGoodbye, matey!")


# --- Entry point ---
if __name__ == "__main__":
    chat_loop()