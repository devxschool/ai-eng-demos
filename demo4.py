from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent


# 1. Tool Creation
@tool
def calculate_salary_range(min_salary: int, max_salary: int, bonus_percentage: float = 10.0) -> dict:
    """Calculate total compensation range including bonus.
    
    Args:
        min_salary: Minimum base salary
        max_salary: Maximum base salary  
        bonus_percentage: Bonus as percentage of salary (default 10%)
    
    Returns:
        Dictionary with compensation details
    """
    min_total = min_salary * (1 + bonus_percentage / 100)
    max_total = max_salary * (1 + bonus_percentage / 100)
    
    return {
        "base_range": f"${min_salary:,} - ${max_salary:,}",
        "total_comp_range": f"${min_total:,.0f} - ${max_total:,.0f}",
        "bonus_percentage": bonus_percentage
    }
    

# 2. Model Setup and Agent Creation with Automatic Tool Execution
model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)
tools = [calculate_salary_range]

# Create a ReAct agent that automatically executes tools
agent = create_react_agent(model, tools)

# 3. Automatic Tool Execution
user_input = "What would be the total compensation for a software engineer role with base salary between 80k and 120k?"

# The agent will automatically call and execute tools as needed
result = agent.invoke({"messages": [HumanMessage(content=user_input)]})

print("Final response:")
print(result["messages"][-1].content)

print("\nFull conversation:")
for i, message in enumerate(result["messages"]):
    print(f"{i+1}. {message.__class__.__name__}: {message.content}")