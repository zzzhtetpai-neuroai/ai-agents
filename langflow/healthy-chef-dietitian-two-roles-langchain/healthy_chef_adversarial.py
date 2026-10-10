# Two-role recipe generator: Chef creates, Dietitian makes it healthier
# Setup: uv pip install langchain-openai langchain-core python-dotenv
# Key goes in a .env file as OPENAI_API_KEY=...

# --- Imports ---
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# --- Load the API key ---
load_dotenv()

# Stop right away if the key is missing
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Set OPENAI_API_KEY before running this script.")

# --- Model ---
# One model used for both roles, called twice in a row
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# --- Chef prompt ---
# Blank: what the user typed (recipe name and/or ingredients)
chef_prompt = PromptTemplate(
    input_variables=["user_input"],
    template=(
        "Act as a world-renowned Chef. Given the input from the user which might "
        "contain the title of a desired recipe and/or some ingredients available to use:\n\n"
        "{user_input}\n\n"
        "create a detailed recipe following the format:\n\n"
        "TITLE: A recipe title.\n"
        "INGREDIENTS: A list of ingredients with quantities.\n"
        "PREPARATION: Step-by-step preparation instructions.\n\n"
        "Ensure the recipe is creative and appealing. Just generate the recipe using the "
        "given format. If the input is insufficient, output \"Insufficient input\"."
    ),
)

# --- Dietitian prompt ---
# Blank: the chef's recipe, which gets reviewed and improved
dietitian_prompt = PromptTemplate(
    input_variables=["chef_output"],
    template=(
        "You are a Registered Dietitian reviewing the following recipe:\n"
        "---\n"
        "{chef_output}\n"
        "---\n"
        "Evaluate its health aspects and generate a healthier alternative by:\n"
        "- Reducing added sugars and unhealthy fats.\n"
        "- Suggesting substitutions for processed ingredients.\n"
        "- Suggesting different cooking steps to make it healthier.\n\n"
        "The output must follow the format:\n\n"
        "TITLE: The recipe title. It should be as close as possible to the original. "
        "Keep it the same if it applies.\n"
        "INGREDIENTS: A list of ingredients with quantities.\n"
        "PREPARATION: Step-by-step preparation instructions.\n"
        "HEALTH COMMENTS: A paragraph describing why the recipe is healthy and "
        "suggesting ways to make it even healthier (if applicable).\n\n"
        "Just generate an output using the given format. If the input is insufficient, "
        "output \"Insufficient input\"."
    ),
)


# --- Chain the two roles ---
def generate_recipes(user_input: str) -> tuple[str, str]:
    # Step 1: chef writes a recipe from the user's input
    chef_response = llm.invoke(chef_prompt.format(user_input=user_input))
    # Step 2: chef's recipe becomes the dietitian's input
    dietitian_response = llm.invoke(
        dietitian_prompt.format(chef_output=chef_response.content)
    )
    # Return both versions so they can be compared
    return chef_response.content, dietitian_response.content


# --- Terminal loop ---
def chat_loop() -> None:
    try:
        # Keep asking for ideas until Ctrl+C
        while True:
            user_input = input("Ingredients or recipe idea: ")
            chef_recipe, healthy_recipe = generate_recipes(user_input)

            # Show original and healthier version one after another
            print("\n--- Chef's Recipe ---")
            print(chef_recipe)
            print("\n--- Healthier Version ---")
            print(healthy_recipe)
            print("\n")
    # Exit cleanly on Ctrl+C
    except KeyboardInterrupt:
        print("\nHappy cooking!")


# --- Entry point ---
if __name__ == "__main__":
    chat_loop()