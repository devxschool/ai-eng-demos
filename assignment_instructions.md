# Take-Home Assignment: AI Job Application Agent

## Learning Objectives
By completing this assignment, you will learn to:
- Create custom tools using LangChain's `@tool` decorator
- Build and use ReAct agents with LangGraph
- Implement web scraping for job posting data extraction
- Automate form filling using Selenium WebDriver
- Handle JSON data structures and validation
- Integrate multiple tools into a cohesive AI agent workflow

## Assignment Overview
You will build an AI agent system that can:
1. Extract job application requirements from Ashby job posting links
2. Automatically fill out job application forms using dummy profile data

## Requirements

### Part 1: Job Data Extraction Tool
Create a tool that extracts all required fields from an Ashby job posting URL.

**Function Signature:**
```python
@tool
def extract_job_requirements(job_url: str) -> dict:
```

**Expected Output:**
```json
{
    "job_title": "Software Engineer",
    "company": "TechCorp",
    "required_fields": [
        {"field_name": "first_name", "field_type": "text", "required": true},
        {"field_name": "last_name", "field_type": "text", "required": true},
        {"field_name": "email", "field_type": "email", "required": true},
        {"field_name": "phone", "field_type": "tel", "required": false},
        {"field_name": "resume", "field_type": "file", "required": true},
        {"field_name": "cover_letter", "field_type": "textarea", "required": false}
    ],
    "application_url": "https://jobs.ashbyhq.com/company/apply/..."
}
```

### Part 2: Form Filling Tool
Create a tool that fills out the application form using the extracted requirements and dummy profile data.

**Function Signature:**
```python
@tool
def fill_application_form(job_requirements_json: str, dummy_profile_json: str) -> dict:
```

**Requirements:**
- Use Selenium WebDriver in non-headless mode (visible browser)
- Fill all available fields from the dummy profile
- Handle different input types (text, email, tel, file, textarea, select)
- **DO NOT** click the submit button
- Return a summary of what was filled

### Part 3: ReAct Agent Integration
Create a ReAct agent that uses both tools to complete the full workflow.

## Technical Requirements

### Dependencies
```python
langchain
langchain-openai
langgraph
selenium
beautifulsoup4
requests
```

### Browser Setup
- Install ChromeDriver or use selenium-manager
- Ensure Chrome browser is installed

### Dummy Profile Data
Create realistic dummy data including:
- Personal information (name, email, phone)
- Resume file path (create a sample PDF)
- Cover letter text
- Work experience
- Education details

## Deliverables

1. **`job_extraction_tool.py`** - Contains the job requirements extraction tool
2. **`form_filling_tool.py`** - Contains the form filling automation tool
3. **`main_agent.py`** - ReAct agent that orchestrates both tools
4. **`dummy_profile.json`** - Sample profile data
5. **`sample_resume.pdf`** - A simple PDF resume for testing
6. **`requirements.txt`** - All necessary dependencies
7. **`README.md`** - Instructions for running your solution

## Evaluation Criteria

### Technical Implementation (60%)
- Correct use of `@tool` decorator and function signatures
- Proper web scraping implementation with error handling
- Selenium automation that handles various input types
- Clean, readable, and well-documented code

### ReAct Agent Integration (20%)
- Successful integration of tools with LangGraph
- Proper message handling and conversation flow
- Error handling and edge cases

### Code Quality (20%)
- Code organization and structure
- Error handling and validation
- Documentation and comments
- Following Python best practices

## Bonus Points
- Handle dynamic form fields (dropdowns, checkboxes)
- Implement retry logic for failed extractions
- Add logging for debugging
- Handle multiple job posting formats
- Create unit tests for your tools

## Submission Guidelines
1. Create a GitHub repository with your solution
2. Include all required files listed in deliverables
3. Test your solution with at least 2 different Ashby job postings
4. Submit the repository link

## Sample Usage
Your final solution should work like this:
```python
# Example interaction
user_input = "Please extract job requirements from https://jobs.ashbyhq.com/example-job and fill out the application with my dummy profile"

result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
print(result["messages"][-1].content)
```

## Important Notes
- **DO NOT** submit actual job applications during testing
- Use only publicly available job postings for testing
- Respect website rate limits and terms of service
- Include proper error handling for network issues
- Test with job postings that have different field requirements

## Resources
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/tools/)
- [LangGraph ReAct Agent](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [Selenium WebDriver Guide](https://selenium-python.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

Good luck with your assignment! Remember to start early and test frequently. 