"""
Example 7: Testing & Monitoring Chains
Demonstrates how to test chains using FakeListLLM for predictable responses.
"""

from langchain.chains import SequentialChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.fake import FakeListLLM

print("=== Testing Chains with Fake LLM ===")

# Create a fake LLM with predefined responses
fake_llm = FakeListLLM(responses=[
    "Amazing AI-Powered Pizza Ovens: The Future of Food!",  # Title response
    """Here's a 5-bullet outline:
• Introduction to AI-powered pizza ovens
• How machine learning optimizes cooking temperature
• Computer vision for perfect crust detection
• Automated ingredient dispensing systems
• Future implications for the food industry"""  # Outline response
])

# Create the same chains as in example 2, but with fake LLM
title_chain = LLMChain(
    llm=fake_llm,
    prompt=PromptTemplate.from_template("Give me a punchy blog-post title about {idea}."),
    output_key="title",
)

outline_chain = LLMChain(
    llm=fake_llm,
    prompt=PromptTemplate.from_template("Create a 5-bullet outline for '{title}'."),
    output_key="outline",
)

# Create the test pipeline
test_pipeline = SequentialChain(
    chains=[title_chain, outline_chain],
    input_variables=["idea"],
    output_variables=["title", "outline"],
    verbose=True,
)

# Run the test
print("Running test with fake LLM...")
result = test_pipeline({"idea": "AI-powered pizza ovens"})

# Assertions for testing
print("\n=== Test Results ===")
print("Title:", result["title"])
print("Outline:", result["outline"])

# Unit test assertions
expected_title = "Amazing AI-Powered Pizza Ovens: The Future of Food!"
assert result["title"] == expected_title, f"Expected '{expected_title}' but got '{result['title']}'"
print("✅ Title test passed!")

assert "AI-powered pizza ovens" in result["outline"], "Outline should mention AI-powered pizza ovens"
assert "bullet" in result["outline"], "Outline should contain bullet points"
print("✅ Outline test passed!")

print("\n=== All Tests Passed! ===")

# Example of testing with multiple scenarios
print("\n=== Testing Multiple Scenarios ===")

test_scenarios = [
    {
        "input": {"idea": "blockchain coffee"},
        "fake_responses": ["Blockchain Coffee Revolution!", "• Decentralized brewing\n• Smart contracts for beans"]
    },
    {
        "input": {"idea": "quantum computing"},
        "fake_responses": ["Quantum Computing Explained!", "• Quantum bits and superposition\n• Real-world applications"]
    }
]

for i, scenario in enumerate(test_scenarios):
    print(f"\n--- Test Scenario {i+1} ---")
    
    # Create new fake LLM for each scenario
    scenario_llm = FakeListLLM(responses=scenario["fake_responses"])
    
    # Create chains with scenario-specific LLM
    scenario_title_chain = LLMChain(
        llm=scenario_llm,
        prompt=PromptTemplate.from_template("Give me a punchy blog-post title about {idea}."),
        output_key="title",
    )
    
    scenario_outline_chain = LLMChain(
        llm=scenario_llm,
        prompt=PromptTemplate.from_template("Create a 5-bullet outline for '{title}'."),
        output_key="outline",
    )
    
    scenario_pipeline = SequentialChain(
        chains=[scenario_title_chain, scenario_outline_chain],
        input_variables=["idea"],
        output_variables=["title", "outline"],
    )
    
    scenario_result = scenario_pipeline(scenario["input"])
    print(f"Title: {scenario_result['title']}")
    print(f"Outline: {scenario_result['outline']}")

print("\n✅ All scenario tests completed!") 