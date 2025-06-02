from langchain.chat_models import init_chat_model

# Import message types for structuring conversations
from langchain_core.messages import HumanMessage, SystemMessage

#initialize a gpt-4o-mini model from OpenAI
model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0, model_kwargs={"logprobs": True, "top_logprobs": 5})


# Create a conversation with system instruction and user input
message = [
    SystemMessage("Tell me companies industry and last funding round or market cap if public"),
    HumanMessage("Uber")
]

# Send the messages to the model and get a response
response = model.invoke(message)

print(response)