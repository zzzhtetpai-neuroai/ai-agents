#os reads environment variables,dotenv loads the .env file 
import os 
from dotenv import load_dotenv
#ChatOpenAI=the model,message classes=the inputs we send it 
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
# load the API key 
# read .env into environment variables and grab the key 
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# stop right away if the key is not missing
if not api_key:
    raise RuntimeError("Set the OPENAI_API_KEY first.")
#create the model low temperature = more consistent
llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.1)
#system message to tell the model how to behave
system_msg = SystemMessage(content="Always answer in Pirate English")
#Chat loop
def chat_loop() -> None:
    try:
        # Keep chatting until the user presses Ctrl+C
        while True:
            # get user input from the terminal
            user_input = input("User: ")
            # Send system prompt + latest message to the model (no memory of past turns)
            response  = llm.invoke([system_msg, HumanMessage(content=user_input)])
             # Print only the text part of the reply
            print("AI:", response.content)
    # Exit cleanly on Ctrl+C instead of showing an error
    except KeyboardInterrupt:
        print("\nGoodbye, matey!")


# --- Entry point ---
# Run the chat only when this file is executed directly, not when imported
if __name__ == "__main__":
    chat_loop()

