from langchain.chat_models import init_chat_model

# Import message types for structuring conversations
from langchain_core.messages import HumanMessage, SystemMessage

from typing import Optional

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate


#initialize a gpt-4o-mini model from OpenAI
model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)


class PublicCompanyInfo(BaseModel):
    """Detailed info about a public company"""

    name: str = Field(description="name of the company")
    tickerSymbol: str = Field(description="The ticker symbol of the company on NYSE")
    marketCap: float = Field(description="the current market cap of the company")




system_template = "Give me  the following info about the given company: {specific_info_about_company}, from this up to date company info: {specific_info_about_company}={value}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{company_name}")]
)

structured_llm = model.with_structured_output(PublicCompanyInfo)

prompt = prompt_template.invoke({"specific_info_about_company": "market cap and ticker symbol", "value" :"Public company", "company_name": "Lyft"})

response = structured_llm.invoke(prompt)

print(response)