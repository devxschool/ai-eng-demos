from langchain_core.tools import tool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def fill_application_form(job_requirements_json: str, dummy_profile_json: str) -> dict:
    """Fill out a job application form using extracted requirements and dummy profile.
    
    Args:
        job_requirements_json: JSON string containing job requirements from extract_job_requirements
        dummy_profile_json: JSON string containing dummy profile data
        
    Returns:
        Dictionary with summary of filled fields and any errors
    """
    try:
        # Parse JSON inputs
        job_requirements = json.loads(job_requirements_json)
        dummy_profile = json.loads(dummy_profile_json)
        
        # Set up Chrome driver (non-headless mode as required)
        chrome_options = Options()
        # Note: DO NOT add --headless option as assignment requires visible browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to application URL
            application_url = job_requirements.get("application_url")
            if not application_url:
                return {"error": "No application URL found in job requirements"}
            
            logger.info(f"Navigating to: {application_url}")
            driver.get(application_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            filled_fields = []
            errors = []
            
            # Iterate through required fields and fill them
            for field in job_requirements.get("required_fields", []):
                field_name = field.get("field_name")
                field_type = field.get("field_type")
                
                try:
                    success = _fill_field(driver, field, dummy_profile)
                    if success:
                        filled_fields.append(field_name)
                    else:
                        errors.append(f"Failed to fill field: {field_name}")
                except Exception as e:
                    errors.append(f"Error filling {field_name}: {str(e)}")
            
            # Wait a moment to see the filled form
            time.sleep(3)
            
            # DO NOT SUBMIT - as per assignment requirements
            logger.info("Form filling completed. NOT submitting as per requirements.")
            
            return {
                "status": "completed",
                "job_title": job_requirements.get("job_title"),
                "company": job_requirements.get("company"),
                "filled_fields": filled_fields,
                "errors": errors,
                "total_fields": len(job_requirements.get("required_fields", [])),
                "successfully_filled": len(filled_fields)
            }
            
        finally:
            # Keep browser open for a few seconds to see results
            time.sleep(5)
            driver.quit()
            
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON input: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def _fill_field(driver: webdriver.Chrome, field: dict, profile: dict) -> bool:
    """Fill a single form field based on its type and profile data.
    
    Args:
        driver: Selenium WebDriver instance
        field: Dictionary containing field information
        profile: Dictionary containing profile data
        
    Returns:
        True if field was successfully filled, False otherwise
    """
    field_name = field.get("field_name")
    field_type = field.get("field_type")
    
    # TODO: Implement field filling logic
    # Hints:
    # 1. Use various locator strategies (name, id, xpath, css_selector)
    # 2. Handle different input types:
    #    - text, email, tel: Use send_keys()
    #    - textarea: Use send_keys()
    #    - select: Use Select class
    #    - file: Use send_keys() with file path
    #    - checkbox/radio: Use click()
    # 3. Map field names to profile data
    # 4. Add proper wait conditions
    # 5. Handle cases where field is not found
    
    try:
        # Example implementation structure:
        element = None
        
        # Try different locator strategies
        locators = [
            (By.NAME, field_name),
            (By.ID, field_name),
            (By.CSS_SELECTOR, f"input[name='{field_name}']"),
            (By.CSS_SELECTOR, f"#{field_name}"),
            (By.XPATH, f"//input[@placeholder='{field_name}']")
        ]
        
        for locator_type, locator_value in locators:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
                break
            except:
                continue
        
        if not element:
            logger.warning(f"Could not find element for field: {field_name}")
            return False
        
        # Get corresponding value from profile
        profile_value = _get_profile_value(field_name, profile)
        if not profile_value:
            logger.warning(f"No profile value found for field: {field_name}")
            return False
        
        # Fill based on field type
        if field_type in ["text", "email", "tel"]:
            element.clear()
            element.send_keys(profile_value)
        elif field_type == "textarea":
            element.clear()
            element.send_keys(profile_value)
        elif field_type == "file":
            element.send_keys(profile_value)  # Should be file path
        elif field_type == "select":
            select = Select(element)
            select.select_by_visible_text(profile_value)
        # TODO: Add more field types as needed
        
        logger.info(f"Successfully filled field: {field_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error filling field {field_name}: {e}")
        return False

def _get_profile_value(field_name: str, profile: dict) -> str:
    """Map field names to profile values.
    
    Args:
        field_name: Name of the form field
        profile: Dictionary containing profile data
        
    Returns:
        Corresponding value from profile or empty string
    """
    # TODO: Implement field name mapping
    # Hints:
    # 1. Create a mapping dictionary from field names to profile keys
    # 2. Handle variations in field naming (first_name, firstName, fname, etc.)
    # 3. Return appropriate default values for missing data
    
    field_mapping = {
        "first_name": profile.get("first_name", ""),
        "last_name": profile.get("last_name", ""),
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "resume": profile.get("resume_path", ""),
        "cover_letter": profile.get("cover_letter", ""),
        # TODO: Add more mappings
    }
    
    return field_mapping.get(field_name, "")

# Test function for development
if __name__ == "__main__":
    # Sample test data
    job_requirements = {
        "job_title": "Software Engineer",
        "company": "TechCorp",
        "application_url": "https://example.com/apply",
        "required_fields": [
            {"field_name": "first_name", "field_type": "text", "required": True},
            {"field_name": "email", "field_type": "email", "required": True}
        ]
    }
    
    dummy_profile = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    
    result = fill_application_form(
        json.dumps(job_requirements),
        json.dumps(dummy_profile)
    )
    print(json.dumps(result, indent=2)) 