from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def extract_job_requirements(job_url: str) -> dict:
    """Extract all required fields from an Ashby job posting URL.
    
    Args:
        job_url: The URL of the Ashby job posting
        
    Returns:
        Dictionary containing job title, company, required fields, and application URL
    """
    try:
        # TODO: Implement web scraping logic
        # Hints:
        # 1. Send GET request to the job_url
        # 2. Parse HTML with BeautifulSoup
        # 3. Extract job title and company name
        # 4. Find the application form or application URL
        # 5. If there's a separate application page, scrape that too
        # 6. Identify form fields and their attributes
        # 7. Return structured data as specified in the assignment
        
        # Example implementation structure:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(job_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic job information
        job_title = "TODO: Extract job title"
        company = "TODO: Extract company name"
        
        # Find application URL or form
        application_url = "TODO: Extract application URL"
        
        # Extract form fields
        required_fields = []
        # TODO: Parse form fields and determine their types and requirements
        
        return {
            "job_title": job_title,
            "company": company,
            "required_fields": required_fields,
            "application_url": application_url
        }
        
    except requests.RequestException as e:
        logger.error(f"Error fetching job posting: {e}")
        return {"error": f"Failed to fetch job posting: {str(e)}"}
    except Exception as e:
        logger.error(f"Error parsing job posting: {e}")
        return {"error": f"Failed to parse job posting: {str(e)}"}

def _parse_form_fields(soup: BeautifulSoup) -> List[Dict]:
    """Helper function to parse form fields from HTML.
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        List of dictionaries containing field information
    """
    fields = []
    
    # TODO: Implement form field parsing logic
    # Hints:
    # 1. Look for input, textarea, select elements
    # 2. Extract name/id, type, required attributes
    # 3. Handle different input types appropriately
    # 4. Check for labels to get field descriptions
    
    return fields

# Test function for development
if __name__ == "__main__":
    # Test with a sample Ashby job URL
    test_url = "https://jobs.ashbyhq.com/sample-job"  # Replace with actual URL
    result = extract_job_requirements(test_url)
    print(json.dumps(result, indent=2)) 