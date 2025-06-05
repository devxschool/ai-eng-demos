from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
import traceback
import logging
import json
import os
from datetime import datetime
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for structured output
class FormField(BaseModel):
    """Individual form field with locator information"""
    field_name: str = Field(description="Human-readable field name")
    field_type: str = Field(description="Input type (text, email, select, textarea, etc.)")
    locator_type: str = Field(description="Selenium locator type (id, name, xpath, css_selector)")
    locator_value: str = Field(description="The actual locator string")
    is_required: bool = Field(description="Whether field is mandatory")
    placeholder_text: str = Field(description="Any placeholder or help text", default="")
    options: List[str] = Field(description="Available options for select fields", default=[])

class FileUploadField(BaseModel):
    """File upload field information"""
    field_name: str = Field(description="Upload field name (resume, cover letter, etc.)")
    locator_type: str = Field(description="Selenium locator type")
    locator_value: str = Field(description="The actual locator string")
    accepted_formats: List[str] = Field(description="Accepted file formats", default=[])
    is_required: bool = Field(description="Whether upload is mandatory")

class JobApplicationFieldsWithLocators(BaseModel):
    """Complete job application analysis with element locators"""
    job_title: str = Field(description="The job title")
    company_name: str = Field(description="The company name")
    required_fields: List[FormField] = Field(description="All required form fields with locators")
    optional_fields: List[FormField] = Field(description="All optional form fields with locators")
    file_upload_fields: List[FileUploadField] = Field(description="File upload requirements with locators")
    dropdown_options: List[Dict[str, Any]] = Field(description="Dropdown fields with their options")
    extraction_status: str = Field(description="Status of extraction")
    url: str = Field(description="Source URL")

class FormFillingResult(BaseModel):
    """Result of form filling operation"""
    filling_status: str = Field(description="success, partial, or error")
    filled_fields: List[str] = Field(description="Names of successfully filled fields")
    failed_fields: List[Dict[str, str]] = Field(description="Fields that couldn't be filled with error reasons")
    screenshot_path: str = Field(description="Path to screenshot of filled form")
    total_fields: int = Field(description="Total number of fields attempted")
    success_rate: float = Field(description="Percentage of successfully filled fields")

# Initialize LLM for parsing
model = init_chat_model("gpt-4o", model_provider="openai", temperature=0)
# Use JSON mode instead of function calling
structured_llm = model.bind(response_format={"type": "json_object"})

# Dummy profile data
DUMMY_PROFILE = {
    "personal_info": {
        "first_name": "John",
        "last_name": "Doe", 
        "email": "john.doe@email.com",
        "phone": "+1-555-123-4567",
        "linkedin": "https://linkedin.com/in/johndoe",
        "website": "https://johndoe.dev",
        "github": "https://github.com/johndoe"
    },
    "address": {
        "street": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
        "country": "United States"
    },
    "work_authorization": "US Citizen",
    "experience_years": "3-5 years",
    "salary_expectation": "$120,000",
    "availability": "2 weeks notice",
    "education": {
        "degree": "Bachelor of Science",
        "major": "Computer Science",
        "university": "University of California, Berkeley",
        "graduation_year": "2020"
    },
    "skills": "Python, JavaScript, React, Node.js, SQL, AWS",
    "cover_letter": "I am excited to apply for this position and believe my experience in software development makes me a strong candidate.",
    "additional_info": "I am passionate about building scalable applications and have experience working in agile environments."
}

def create_screenshot_dir():
    """Create screenshots directory if it doesn't exist"""
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    return screenshot_dir

def take_screenshot(driver, filename_prefix):
    """Take screenshot and return the file path"""
    screenshot_dir = create_screenshot_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshot_dir, f"{filename_prefix}_{timestamp}.png")
    driver.save_screenshot(screenshot_path)
    logger.info(f"Screenshot saved: {screenshot_path}")
    return screenshot_path

def simulate_human_typing(element, text, typing_delay=0.1):
    """Simulate human-like typing with random delays"""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, typing_delay))

def find_element_with_multiple_strategies(driver, field):
    """Try multiple strategies to find an element"""
    strategies = [
        (field.locator_type, field.locator_value),
        (By.NAME, field.field_name.lower().replace(" ", "_")),
        (By.NAME, field.field_name.lower().replace(" ", "-")),
        (By.ID, field.field_name.lower().replace(" ", "_")),
        (By.ID, field.field_name.lower().replace(" ", "-")),
    ]
    
    # Add xpath strategies for common patterns
    if "name" in field.field_name.lower():
        strategies.extend([
            (By.XPATH, "//input[contains(@placeholder, 'name')]"),
            (By.XPATH, "//input[contains(@aria-label, 'name')]")
        ])
    elif "email" in field.field_name.lower():
        strategies.extend([
            (By.XPATH, "//input[@type='email']"),
            (By.XPATH, "//input[contains(@placeholder, 'email')]")
        ])
    elif "phone" in field.field_name.lower():
        strategies.extend([
            (By.XPATH, "//input[@type='tel']"),
            (By.XPATH, "//input[contains(@placeholder, 'phone')]")
        ])
    
    for strategy in strategies:
        try:
            locator_type, locator_value = strategy
            if locator_type == "css_selector":
                locator_type = By.CSS_SELECTOR
            elif locator_type == "xpath":
                locator_type = By.XPATH
            elif locator_type == "id":
                locator_type = By.ID
            elif locator_type == "name":
                locator_type = By.NAME
            elif locator_type == "class_name":
                locator_type = By.CLASS_NAME
            
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
            logger.info(f"Found element using {locator_type}: {locator_value}")
            return element
        except Exception as e:
            logger.debug(f"Strategy failed {locator_type}:{locator_value} - {str(e)}")
            continue
    
    return None

@tool
def extract_job_application_fields_with_locators(url: str) -> dict:
    """Extract all required fields and their element locators from an Ashby job application page.
    
    Args:
        url: Ashby job application URL (e.g., https://jobs.ashbyhq.com/company/job-id/application)
    
    Returns:
        Dictionary with job info, required fields, optional fields, file uploads, and element locators
    """
    
    # Setup Chrome webdriver with options (headless for extraction)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = None
    try:
        logger.info(f"Starting field extraction for URL: {url}")
        
        # Initialize webdriver
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome webdriver initialized successfully")
        
        # Navigate to the URL
        driver.get(url)
        logger.info(f"Navigated to URL: {url}")
        
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("Page loaded successfully")
        
        # Additional wait for dynamic content
        time.sleep(5)
        
        # Extract page title and HTML content
        page_title = driver.title
        html_content = driver.page_source
        logger.info(html_content)
        logger.info(f"Extracted HTML content, length: {len(html_content)} characters")
        
        # Also extract visible text for better analysis
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Reduce content size to avoid token limits
        # Take first 8000 chars of HTML and first 3000 chars of visible text
        html_sample = html_content[:8000]
        body_sample = body_text[:3000]
        
        # Use LLM to parse the HTML and extract required fields with locators
        prompt = f"""
        You are analyzing an Ashby job application page. Return a JSON object with the exact structure shown below.
        
        Page Title: {page_title}
        
        HTML Content (sample): {html_sample}
        
        
        Please identify and extract information and return it as a JSON object with this exact structure:
        
        {{
            "job_title": "string - The job title from the page",
            "company_name": "string - The company name from the page", 
            "required_fields": [
                {{
                    "field_name": "string - Human readable field name",
                    "field_type": "string - Input type (text, email, tel, select, textarea, etc.)",
                    "locator_type": "string - Selenium locator type (id, name, xpath, css_selector)",
                    "locator_value": "string - The actual locator string",
                    "is_required": true,
                    "placeholder_text": "string - Any placeholder or help text",
                    "options": []
                }}
            ],
            "optional_fields": [
                {{
                    "field_name": "string",
                    "field_type": "string", 
                    "locator_type": "string",
                    "locator_value": "string",
                    "is_required": false,
                    "placeholder_text": "string",
                    "options": []
                }}
            ],
            "file_upload_fields": [
                {{
                    "field_name": "string - Upload field name (resume, cover letter, etc.)",
                    "locator_type": "string",
                    "locator_value": "string", 
                    "accepted_formats": ["pdf", "doc", "docx"],
                    "is_required": true
                }}
            ],
            "dropdown_options": [],
            "extraction_status": "success",
            "url": "{url}"
        }}
        
        Look for:
        1. Form input fields with their HTML attributes (id, name, class)
        2. Required fields (marked with asterisks * or required attributes)
        3. Field types (text, email, tel, select, textarea, checkbox, radio, file)
        4. Placeholder text or labels
        5. File upload requirements
        
        For locators, prioritize: 1) ID attributes, 2) Name attributes, 3) CSS selectors, 4) XPath
        
        Return ONLY the JSON object, no other text.
        """
        
        logger.info("Sending HTML to LLM for parsing")
        # Get response from LLM in JSON mode
        response = structured_llm.invoke(prompt)
        logger.info("LLM parsing completed successfully")
        logger.info(f"LLM response content: {response.content}")
        
        # Parse the JSON response manually
        try:
            result_data = json.loads(response.content)
            logger.info("JSON parsing successful")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.content}")
            raise Exception(f"Invalid JSON response from LLM: {e}")
        
        # Convert to dictionary for return
        return {
            "job_title": result_data.get("job_title", "Could not extract"),
            "company_name": result_data.get("company_name", "Could not extract"),
            "required_fields": result_data.get("required_fields", []),
            "optional_fields": result_data.get("optional_fields", []),
            "file_upload_fields": result_data.get("file_upload_fields", []),
            "dropdown_options": result_data.get("dropdown_options", []),
            "extraction_status": "success",
            "url": url,
            "total_fields": len(result_data.get("required_fields", [])) + len(result_data.get("optional_fields", []))
        }
        
    except Exception as e:
        error_details = {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "traceback": traceback.format_exc(),
            "url": url
        }
        
        logger.error(f"Error extracting job application fields: {error_details}")
        
        # Special handling for token limit errors
        if "LengthFinishReasonError" in str(e) or "length limit" in str(e).lower():
            logger.warning("Token limit reached - trying with even smaller content sample")
            try:
                # Try again with much smaller content
                html_tiny = html_content[:3000]
                body_tiny = body_text[:1000]
                
                simplified_prompt = f"""
                Analyze this Ashby job application page and return a JSON object:
                
                Page: {page_title}
                HTML Sample: {html_tiny}
                Text: {body_tiny}
                
                Return JSON with this structure:
                {{
                    "job_title": "extracted job title or 'Unknown'",
                    "company_name": "extracted company name or 'Unknown'",
                    "required_fields": [],
                    "optional_fields": [],
                    "file_upload_fields": [],
                    "dropdown_options": [],
                    "extraction_status": "partial",
                    "url": "{url}"
                }}
                
                Extract basic job info only. Return ONLY the JSON.
                """
                
                response = structured_llm.invoke(simplified_prompt)
                result_data = json.loads(response.content)
                
                logger.info("Fallback extraction successful with reduced content")
                return {
                    "job_title": result_data.get("job_title", "Could not extract"),
                    "company_name": result_data.get("company_name", "Could not extract"),
                    "required_fields": result_data.get("required_fields", []),
                    "optional_fields": result_data.get("optional_fields", []),
                    "file_upload_fields": result_data.get("file_upload_fields", []),
                    "dropdown_options": result_data.get("dropdown_options", []),
                    "extraction_status": "partial",
                    "url": url,
                    "total_fields": 0,
                    "warning": "Token limit reached - basic extraction only"
                }
            except Exception as fallback_error:
                logger.error(f"Fallback extraction also failed: {fallback_error}")
        
        return {
            "extraction_status": "error",
            "error_type": error_details["exception_type"],
            "error_message": error_details["exception_message"],
            "full_traceback": error_details["traceback"],
            "url": url,
            "job_title": "Could not extract",
            "company_name": "Could not extract",
            "required_fields": [],
            "optional_fields": [],
            "file_upload_fields": [],
            "dropdown_options": [],
            "total_fields": 0
        }
    
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Chrome webdriver closed successfully")
            except Exception as cleanup_error:
                logger.warning(f"Error closing webdriver: {cleanup_error}")

@tool  
def fill_job_application_form(field_data: str, profile_data: str = None) -> dict:
    """Fill out a job application form using extracted field information and profile data.
    
    Args:
        field_data: JSON string containing the output from extract_job_application_fields_with_locators
        profile_data: JSON string with applicant information (optional, uses default if not provided)
    
    Returns:
        Dictionary with filling status, filled fields, failed fields, and screenshot path
    """
    
    try:
        # Parse input data
        fields_info = json.loads(field_data)
        
        if profile_data:
            profile = json.loads(profile_data)
        else:
            profile = DUMMY_PROFILE
            logger.info("Using default dummy profile data")
        
        # Validate field data
        if fields_info.get("extraction_status") != "success":
            return {
                "filling_status": "error",
                "error_message": "Invalid field data - extraction was not successful",
                "filled_fields": [],
                "failed_fields": [],
                "screenshot_path": "",
                "total_fields": 0,
                "success_rate": 0.0
            }
        
        url = fields_info["url"]
        all_fields = fields_info["required_fields"] + fields_info["optional_fields"]
        
        # Setup Chrome webdriver with options (NON-headless for visibility)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        # Explicitly NOT adding --headless to make browser visible
        
        driver = None
        filled_fields = []
        failed_fields = []
        
        try:
            logger.info(f"Starting form filling for URL: {url}")
            
            # Initialize webdriver
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome webdriver initialized successfully (visible mode)")
            
            # Navigate to the URL
            driver.get(url)
            logger.info(f"Navigated to URL: {url}")
            
            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Page loaded successfully")
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Take initial screenshot
            initial_screenshot = take_screenshot(driver, "initial_form")
            
            # Create field mapping from profile data
            field_mapping = {
                # Personal info mappings
                "first name": profile["personal_info"]["first_name"],
                "last name": profile["personal_info"]["last_name"],
                "email": profile["personal_info"]["email"],
                "phone": profile["personal_info"]["phone"],
                "linkedin": profile["personal_info"]["linkedin"],
                "website": profile["personal_info"]["website"],
                "github": profile["personal_info"]["github"],
                
                # Address mappings
                "address": profile["address"]["street"],
                "street": profile["address"]["street"], 
                "city": profile["address"]["city"],
                "state": profile["address"]["state"],
                "zip": profile["address"]["zip_code"],
                "zip code": profile["address"]["zip_code"],
                "country": profile["address"]["country"],
                
                # Work info mappings
                "work authorization": profile["work_authorization"],
                "experience": profile["experience_years"],
                "salary": profile["salary_expectation"],
                "availability": profile["availability"],
                "skills": profile["skills"],
                
                # Education mappings
                "degree": profile["education"]["degree"],
                "major": profile["education"]["major"],
                "university": profile["education"]["university"],
                "graduation": profile["education"]["graduation_year"],
                
                # Text area mappings
                "cover letter": profile["cover_letter"],
                "additional information": profile["additional_info"],
                "why": profile["cover_letter"],
                "motivation": profile["cover_letter"]
            }
            
            # Process each field
            for field_info in all_fields:
                field_name = field_info["field_name"].lower()
                field_type = field_info["field_type"]
                
                try:
                    logger.info(f"Processing field: {field_name} (type: {field_type})")
                    
                    # Find the element
                    element = find_element_with_multiple_strategies(driver, FormField(**field_info))
                    
                    if not element:
                        failed_fields.append({
                            "field_name": field_info["field_name"],
                            "error": "Element not found with any strategy"
                        })
                        continue
                    
                    # Scroll element into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    
                    # Find matching value from profile
                    value_to_fill = None
                    for key, value in field_mapping.items():
                        if key in field_name:
                            value_to_fill = value
                            break
                    
                    if not value_to_fill:
                        # Try partial matches for complex field names
                        for key, value in field_mapping.items():
                            if any(word in field_name for word in key.split()):
                                value_to_fill = value
                                break
                    
                    if not value_to_fill:
                        failed_fields.append({
                            "field_name": field_info["field_name"],
                            "error": "No matching profile data found"
                        })
                        continue
                    
                    # Fill the field based on type
                    if field_type in ["text", "email", "tel", "url", "password"]:
                        simulate_human_typing(element, str(value_to_fill))
                        
                    elif field_type == "textarea":
                        simulate_human_typing(element, str(value_to_fill))
                        
                    elif field_type == "select":
                        select = Select(element)
                        # Try to select by visible text or value
                        try:
                            select.select_by_visible_text(str(value_to_fill))
                        except:
                            try:
                                select.select_by_value(str(value_to_fill))
                            except:
                                # If exact match fails, try first option that contains the value
                                for option in select.options:
                                    if str(value_to_fill).lower() in option.text.lower():
                                        select.select_by_visible_text(option.text)
                                        break
                    
                    elif field_type in ["checkbox", "radio"]:
                        if not element.is_selected():
                            element.click()
                    
                    filled_fields.append(field_info["field_name"])
                    logger.info(f"Successfully filled field: {field_info['field_name']}")
                    
                    # Small delay between fields
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as field_error:
                    logger.error(f"Error filling field {field_info['field_name']}: {str(field_error)}")
                    failed_fields.append({
                        "field_name": field_info["field_name"],
                        "error": str(field_error)
                    })
            
            # Take final screenshot
            final_screenshot = take_screenshot(driver, "filled_form")
            
            # Calculate success rate
            total_fields = len(all_fields)
            success_rate = (len(filled_fields) / total_fields * 100) if total_fields > 0 else 0
            
            # Determine overall status
            if len(filled_fields) == total_fields:
                status = "success"
            elif len(filled_fields) > 0:
                status = "partial"
            else:
                status = "error"
            
            logger.info(f"Form filling completed. Status: {status}, Success rate: {success_rate:.1f}%")
            
            # Keep browser open for a few seconds so user can see the result
            logger.info("Keeping browser open for 5 seconds so you can see the filled form...")
            time.sleep(5)
            
            return {
                "filling_status": status,
                "filled_fields": filled_fields,
                "failed_fields": failed_fields,
                "screenshot_path": final_screenshot,
                "total_fields": total_fields,
                "success_rate": round(success_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error during form filling: {str(e)}")
            
            # Try to take error screenshot
            error_screenshot = ""
            if driver:
                try:
                    error_screenshot = take_screenshot(driver, "error_form")
                except:
                    pass
            
            return {
                "filling_status": "error",
                "error_message": str(e),
                "filled_fields": filled_fields,
                "failed_fields": failed_fields,
                "screenshot_path": error_screenshot,
                "total_fields": len(all_fields),
                "success_rate": 0.0
            }
        
        finally:
            if driver:
                try:
                    # Give user time to see the result before closing
                    logger.info("Browser will close in 3 seconds...")
                    time.sleep(3)
                    driver.quit()
                    logger.info("Chrome webdriver closed successfully")
                except Exception as cleanup_error:
                    logger.warning(f"Error closing webdriver: {cleanup_error}")
    
    except json.JSONDecodeError as e:
        return {
            "filling_status": "error",
            "error_message": f"Invalid JSON data: {str(e)}",
            "filled_fields": [],
            "failed_fields": [],
            "screenshot_path": "",
            "total_fields": 0,
            "success_rate": 0.0
        }
    except Exception as e:
        return {
            "filling_status": "error", 
            "error_message": f"Unexpected error: {str(e)}",
            "filled_fields": [],
            "failed_fields": [],
            "screenshot_path": "",
            "total_fields": 0,
            "success_rate": 0.0
        }

# Test/Demo function
def demo_job_application_automation():
    """Demonstrate the complete workflow of both tools"""
    
    print("=== JOB APPLICATION AUTOMATION DEMO ===\n")
    
    # Test URL
    test_url = "https://jobs.ashbyhq.com/wander/121c24e0-eeff-49a8-ac56-793d2dbc9fcd/application"
    
    print("Step 1: Extracting job application fields and locators...")
    print(f"URL: {test_url}\n")
    
    # Extract fields
    extraction_result = extract_job_application_fields_with_locators.invoke({"url": test_url})
    
    if extraction_result["extraction_status"] == "success":
        print("✅ Field extraction successful!")
        print(f"Job: {extraction_result['job_title']} at {extraction_result['company_name']}")
        print(f"Required fields: {len(extraction_result['required_fields'])}")
        print(f"Optional fields: {len(extraction_result['optional_fields'])}")
        print(f"File uploads: {len(extraction_result['file_upload_fields'])}")
        print()
        
        print("Step 2: Filling out the job application form...")
        print("Using dummy profile data...\n")
        
        # Convert to JSON string for the tool
        field_data_json = json.dumps(extraction_result)
        
        # Fill the form
        filling_result = fill_job_application_form.invoke({"field_data": field_data_json})
        
        print("✅ Form filling completed!")
        print(f"Status: {filling_result['filling_status']}")
        print(f"Successfully filled: {len(filling_result['filled_fields'])} fields")
        print(f"Failed to fill: {len(filling_result['failed_fields'])} fields")
        print(f"Success rate: {filling_result['success_rate']}%")
        
        if filling_result['screenshot_path']:
            print(f"Screenshot saved: {filling_result['screenshot_path']}")
        
        if filling_result['failed_fields']:
            print("\nFailed fields:")
            for failed in filling_result['failed_fields']:
                print(f"  - {failed['field_name']}: {failed['error']}")
        
    else:
        print("❌ Field extraction failed!")
        print(f"Error: {extraction_result.get('error_message', 'Unknown error')}")

if __name__ == "__main__":
    demo_job_application_automation()
