# Pirate Style Chatbot (LangChain)

Two versions of a terminal chatbot that always replies in Pirate English, showing how a chatbot goes from no memory to remembering the conversation.

## Files

### `pirate_chatbot_basic.py`
- Uses a system message to control the bot's personality
- Sends only the latest user message each turn
- No memory: it forgets everything after each reply

### `pirate_chatbot_with_memory.py`
- Stores every turn in a history list
- Uses a PromptTemplate to combine the history with the new message
- The model "remembers" by rereading the whole conversation each turn

## Key concepts
- System prompt vs user message
- Temperature (low = consistent answers)
- Why LLMs have no built-in memory, and how history injection fixes it

## Run

```bash
python pirate_chatbot_basic.py
python pirate_chatbot_with_memory.py
```

Test memory: tell it your name, then ask "what's my name?" Stop with Ctrl+C.
