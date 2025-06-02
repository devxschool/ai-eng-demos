from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydantic import BaseModel, Field
from typing import List, Optional
import time
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic model for structured output
class JobApplicationFields(BaseModel):
    """Required fields for job application"""
    
    required_fields: List[str] = Field(description="List of all required field names/labels")
    optional_fields: List[str] = Field(description="List of all optional field names/labels")
    file_uploads: List[str] = Field(description="List of file upload requirements (resume, cover letter, etc.)")
    questions: List[str] = Field(description="List of specific questions that need answers")
    job_title: str = Field(description="The job title")
    company_name: str = Field(description="The company name")

# Initialize LLM for parsing
model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)
structured_llm = model.with_structured_output(JobApplicationFields, method="function_calling")

# Core extraction function (not decorated as tool)
def _extract_job_application_info_core(url: str, raise_on_error: bool = False) -> dict:
    """Core extraction logic that can be called directly or wrapped as a tool"""
    
    # Setup Chrome webdriver with options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        logger.info(f"Starting extraction for URL: {url}")
        
        # Initialize webdriver
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome webdriver initialized successfully")
        
        # Navigate to the URL
        driver.get(url)
        logger.info(f"Navigated to URL: {url}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("Page loaded successfully")
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Extract HTML content
        html_content = driver.page_source
        logger.info(f"Extracted HTML content, length: {len(html_content)} characters")
        
        # Use LLM to parse the HTML and extract required fields
        prompt = f"""
        Analyze this Ashby job application page HTML and extract all required information:
        
        {html_content}
        
        Please identify:
        1. All required fields (marked with asterisks * or required indicators)
        2. All optional fields
        3. File upload requirements (resume, cover letter, portfolio, etc.)
        4. Any specific questions that need answers
        5. Job title and company name
        
        Focus on form fields, input elements, and application requirements.
        """
        
        logger.info("Sending HTML to LLM for parsing")
        # Get structured response from LLM
        result = structured_llm.invoke(prompt)
        logger.info("LLM parsing completed successfully")
        
        # Convert to dictionary for return
        return {
            "job_title": result.job_title,
            "company_name": result.company_name,
            "required_fields": result.required_fields,
            "optional_fields": result.optional_fields,
            "file_uploads": result.file_uploads,
            "questions": result.questions,
            "url": url,
            "extraction_status": "success"
        }
        
    except Exception as e:
        # Get full exception details
        error_details = {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "traceback": traceback.format_exc(),
            "url": url
        }
        
        # Log the full error
        logger.error(f"Error extracting job application info: {error_details}")
        
        # If raise_on_error is True, re-raise the exception with additional context
        if raise_on_error:
            raise Exception(f"Failed to extract job application info from {url}. "
                          f"Error: {type(e).__name__}: {str(e)}\n"
                          f"Full traceback:\n{traceback.format_exc()}") from e
        
        # Otherwise return detailed error information
        return {
            "extraction_status": "error",
            "error_type": error_details["exception_type"],
            "error_message": error_details["exception_message"],
            "full_traceback": error_details["traceback"],
            "url": url,
            "required_fields": [],
            "optional_fields": [],
            "file_uploads": [],
            "questions": [],
            "job_title": "Could not extract",
            "company_name": "Could not extract"
        }
    
    finally:
        # Clean up webdriver
        if driver:
            try:
                driver.quit()
                logger.info("Chrome webdriver closed successfully")
            except Exception as cleanup_error:
                logger.warning(f"Error closing webdriver: {cleanup_error}")

##create a tool that genates application info - https://jobs.ashbyhq.com/wander/121c24e0-eeff-49a8-ac56-793d2dbc9fcd/application
@tool
def extract_required_job_application_information(url: str) -> dict:
    """Go to Ashby job posting via provided link, read the html and return all required fields
    
    Args:
        url: Ashby Job posting URL
    
    Returns:
        Dictionary with all required info.
    """
    # Call the core function without raise_on_error (tools should be robust)
    return _extract_job_application_info_core(url, raise_on_error=False)

# Test the tool
if __name__ == "__main__":
    test_url = "https://jobs.ashbyhq.com/wander/121c24e0-eeff-49a8-ac56-793d2dbc9fcd/application"
    
    print("=== TESTING WITH ERROR HANDLING ===")
    result = _extract_job_application_info_core(test_url, raise_on_error=False)
    
    if result["extraction_status"] == "error":
        print("=== ERROR DETAILS ===")
        print(f"Error Type: {result['error_type']}")
        print(f"Error Message: {result['error_message']}")
        print(f"Full Traceback:\n{result['full_traceback']}")
    else:
        print("=== JOB APPLICATION REQUIREMENTS ===")
        print(f"Job Title: {result['job_title']}")
        print(f"Company: {result['company_name']}")
        print(f"\nRequired Fields: {result['required_fields']}")
        print(f"\nOptional Fields: {result['optional_fields']}")
        print(f"\nFile Uploads: {result['file_uploads']}")
        print(f"\nQuestions: {result['questions']}")
        print(f"\nStatus: {result['extraction_status']}")
    
    print("\n=== TESTING WITH EXCEPTION RAISING ===")
    try:
        result = _extract_job_application_info_core(test_url, raise_on_error=True)
        print("Success!")
    except Exception as e:
        print(f"Exception caught: {e}")
    
    print("\n=== TESTING TOOL FUNCTION ===")
    # Test the actual tool function
    result = extract_required_job_application_information.invoke({"url": test_url})
    print(f"Tool result status: {result['extraction_status']}")



## create a toll that uses the application info to fill out a job application

