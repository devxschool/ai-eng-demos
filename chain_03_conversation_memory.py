"""
Example 3: Adding Memory (Conversation Flow)
Demonstrates how to use ConversationChain with memory to maintain context.
"""

from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

# Create a conversation chain with memory
chat_bot = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory(return_messages=True),
    verbose=True,
)

print("=== Conversation Chain with Memory ===")

# First interaction
print("\n--- First message ---")
response1 = chat_bot.run("Hi, who are you?")
print("Bot:", response1)

# Second interaction - bot should remember the previous conversation
print("\n--- Second message ---")
response2 = chat_bot.run("What did I just ask?")
print("Bot:", response2)

# Show the conversation history
print("\n--- Conversation History ---")
print(chat_bot.memory.buffer) 