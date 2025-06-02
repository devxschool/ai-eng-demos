from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import HumanMessage


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
    # Step 1: Create prompt
    prompt = prompt_template.invoke({
        "company_name": company_name,
        "target_position": target_position,
        "candidate_background": candidate_background
    })
    
    # Step 2: Get AI response with tool calling
    response = model_with_tools.invoke(prompt.to_messages())
    
    # Step 3: Apply structured output to the final strategy
    structured_model = model.with_structured_output(JobApplicationStrategy)
    
    # Create final structured strategy prompt
    strategy_prompt = f"""Based on this research and analysis: {response.content}
    
    Create a structured job application strategy for {company_name} - {target_position} position."""
    
    structured_strategy = structured_model.invoke(strategy_prompt)
    
    return {
        "research_response": response.content,
        "tool_calls_made": response.tool_calls,
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
print("\n=== TOOL CALLS MADE ===")
print(result["tool_calls_made"])
print("\n=== STRUCTURED STRATEGY ===")
print(result["structured_strategy"])


@tool
def salary_benchmarking(position: str, location: str = "San Francisco") -> dict:
    """Get salary benchmarking data for a position in a location."""
    # Simulated salary data
    salary_data = {
        ("ai research engineer", "san francisco"): {"min": 180000, "max": 300000, "median": 220000},
        ("software engineer", "san francisco"): {"min": 140000, "max": 250000, "median": 180000},
        ("data scientist", "san francisco"): {"min": 130000, "max": 220000, "median": 160000}
    }
    
    key = (position.lower(), location.lower())
    return salary_data.get(key, {"min": 80000, "max": 150000, "median": 110000})

@tool  
def skill_gap_analysis(required_skills: List[str], candidate_skills: List[str]) -> dict:
    """Analyze skill gaps between job requirements and candidate skills."""
    required_set = set(skill.lower() for skill in required_skills)
    candidate_set = set(skill.lower() for skill in candidate_skills)
    
    matching_skills = list(required_set.intersection(candidate_set))
    missing_skills = list(required_set - candidate_set)
    extra_skills = list(candidate_set - required_set)
    
    match_percentage = len(matching_skills) / len(required_skills) * 100 if required_skills else 0
    
    return {
        "match_percentage": round(match_percentage, 1),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills
    }

# Combine multiple tools
tools = [research_company_info, salary_benchmarking, skill_gap_analysis]
model_with_tools = model.bind_tools(tools)

# Enhanced structured output
class ComprehensiveJobAnalysis(BaseModel):
    """Complete job opportunity analysis"""
    
    company_fit_score: float = Field(description="How well you fit the company (1-10)")
    salary_competitiveness: str = Field(description="How competitive the salary range is")
    skill_match_summary: str = Field(description="Summary of skill alignment")
    application_priority: str = Field(description="High/Medium/Low priority for application")
    preparation_timeline: str = Field(description="Recommended timeline for application prep")
    success_probability: str = Field(description="Estimated probability of success")

# Usage with multiple tool calls
user_query = """Analyze this job opportunity:
Company: Google
Position: AI Research Engineer  
Required Skills: Python, TensorFlow, PyTorch, Machine Learning, PhD
My Skills: Python, TensorFlow, Deep Learning, NLP, PhD in CS
Location: San Francisco"""

response = model_with_tools.invoke([HumanMessage(content=user_query)])
print("Analysis with multiple tool calls:")
print(response.content)