from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from langgraph.prebuilt import create_react_agent

# 1. Tool Creation - Company Research
@tool
def research_company_info(company_name: str, info_type: str = "overview") -> dict:
    """Research company information for job applications.
    
    Args:
        company_name: Name of the company to research
        info_type: Type of info needed (overview, culture, benefits, recent_news)
    
    Returns:
        Dictionary with company information
    """
    # Simulated company database
    company_data = {
        "google": {
            "overview": "Tech giant specializing in search, cloud, and AI",
            "culture": "Innovation-driven, data-focused, collaborative",
            "benefits": "Competitive salary, stock options, excellent healthcare, free meals",
            "recent_news": "Major AI breakthroughs with Gemini model, cloud growth"
        },
        "openai": {
            "overview": "AI research company focused on safe AGI development",
            "culture": "Research-oriented, mission-driven, cutting-edge",
            "benefits": "Equity participation, learning opportunities, flexible work",
            "recent_news": "GPT-4 improvements, new reasoning models, partnerships"
        }
    }
    
    company_key = company_name.lower()
    if company_key in company_data:
        return {
            "company": company_name,
            "info_type": info_type,
            "data": company_data[company_key].get(info_type, "Information not available")
        }
    else:
        return {
            "company": company_name,
            "info_type": info_type,
            "data": "Company not found in database"
        }

# 2. Structured Output Model
class JobApplicationStrategy(BaseModel):
    """Strategy for job application based on company research"""
    
    company_name: str = Field(description="Name of the target company")
    key_selling_points: List[str] = Field(description="Your strengths that align with company needs")
    cover_letter_focus: str = Field(description="Main theme for cover letter")
    interview_preparation: List[str] = Field(description="Key areas to prepare for interview")
    questions_to_ask: List[str] = Field(description="Good questions to ask the interviewer")

# 3. Model Setup with Tools and Structured Output
model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)
tools = [research_company_info]
model_with_tools = model.bind_tools(tools)

# 4. ChatPromptTemplate
system_template = """You are a career counselor helping job seekers create application strategies.

First, research the company using the available tools to gather relevant information.
Then, create a personalized job application strategy based on:
- Company culture and values
- Recent company developments  
- The candidate's background: {candidate_background}
- Target position: {target_position}

Use the research tool to gather company information before providing your strategy."""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", "Help me create an application strategy for {company_name} for a {target_position} role.")
])

# 5. Combined Implementation
def create_application_strategy(company_name: str, target_position: str, candidate_background: str):
    # Create an agent that executes tools
    agent = create_react_agent(model, tools)
    
    prompt = prompt_template.invoke({
        "company_name": company_name,
        "target_position": target_position,
        "candidate_background": candidate_background
    })
    
    # Agent will execute tools and provide final response
    agent_response = agent.invoke({"messages": prompt.to_messages()})
    final_message = agent_response["messages"][-1].content
    
    # Step 3: Apply structured output to the final strategy
    structured_model = model.with_structured_output(JobApplicationStrategy)
    
    # Create final structured strategy prompt
    strategy_prompt = f"""Based on this research and analysis: {final_message}
    
    Create a structured job application strategy for {company_name} - {target_position} position."""
    
    structured_strategy = structured_model.invoke(strategy_prompt)
    
    return {
        "research_response": final_message,
        "structured_strategy": structured_strategy
    }

# 6. Usage Example
result = create_application_strategy(
    company_name="OpenAI",
    target_position="AI Research Engineer", 
    candidate_background="PhD in Computer Science, 5 years ML experience, published papers in NLP"
)

print("=== RESEARCH & ANALYSIS ===")
print(result["research_response"])
print("\n=== STRUCTURED STRATEGY ===")
print(result["structured_strategy"])