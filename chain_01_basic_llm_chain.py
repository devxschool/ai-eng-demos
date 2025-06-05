"""
Example 1: Your First LLMChain
Demonstrates basic LLMChain usage with a simple prompt template.
"""

from langchain_openai import OpenAI
from langchain import PromptTemplate, LLMChain

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

# Create a prompt template
prompt = PromptTemplate.from_template(
    "List three surprising facts about {topic}."
)

# Create the chain
facts_chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain
print("=== Basic LLMChain Example ===")
result = facts_chain.run({"topic": "black holes"})
print(result) 