from langchain.chat_models import init_chat_model

# Import message types for structuring conversations
from langchain_core.messages import HumanMessage, SystemMessage

#initialize a gpt-4o-mini model from OpenAI
model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0, model_kwargs={"max_tokens": 500, "logprobs": True, "top_logprobs": 5})

from langchain_core.prompts import ChatPromptTemplate

system_template = "Give me  the following info about the given company: {specific_info_about_company}, from this up to date company info: {specific_info_about_company}={value}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{company_name}")]
)


prompt = prompt_template.invoke({"specific_info_about_company": "headcount", "value" :"5,100", "company_name": "openai"})

print(prompt.to_messages())

response = model.invoke(prompt)

print(response.content)

