"""
Example 2: Stitching Steps with SequentialChain
Demonstrates how to chain multiple LLM calls together in sequence.
"""

from langchain_openai import OpenAI
from langchain.chains import SequentialChain, LLMChain
from langchain.prompts import PromptTemplate

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

# Step-1: Generate a catchy title
title_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("Give me a punchy blog-post title about {idea}."),
    output_key="title",
)

# Step-2: Outline based on that title
outline_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("Create a 5-bullet outline for '{title}'."),
    output_key="outline",
)

# Create the sequential chain
blog_pipeline = SequentialChain(
    chains=[title_chain, outline_chain],
    input_variables=["idea"],
    output_variables=["title", "outline"],
    verbose=True,        # stream each step to console
)

# Run the pipeline
print("=== Sequential Chain Example ===")
result = blog_pipeline({"idea": "AI-powered pizza ovens"})
print("\n=== Results ===")
print("Title:", result["title"])
print("\nOutline:", result["outline"]) 