# Job Application Automation Tools

A comprehensive LangChain-based solution for automating Ashby job application analysis and form filling.

## Overview

This project implements two powerful LangChain tools that work together to:

1. **Extract job application fields** with precise element locators from Ashby job posting pages
2. **Automatically fill out application forms** using predefined profile data with human-like interactions

## Features

- 🔍 **Intelligent Field Detection**: Uses GPT-4 to analyze HTML and extract form fields with their exact locators
- 🤖 **Smart Form Filling**: Automatically maps profile data to form fields with multiple fallback strategies
- 📸 **Screenshot Capture**: Takes screenshots before and after form filling for verification
- 🕰️ **Human-like Interactions**: Simulates realistic typing speeds and delays
- 🛡️ **Robust Error Handling**: Comprehensive error handling with detailed logging
- 📊 **Success Metrics**: Provides detailed statistics on filling success rates

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser installed
- ChromeDriver (will be managed automatically)
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd job-application-automation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Verify installation**
```bash
python toolCalling3.py
```

## Usage

### Tool 1: Field Extraction

```python
from toolCalling3 import extract_job_application_fields_with_locators

# Extract fields from an Ashby job application page
result = extract_job_application_fields_with_locators.invoke({
    "url": "https://jobs.ashbyhq.com/company/job-id/application"
})

print(f"Job: {result['job_title']} at {result['company_name']}")
print(f"Required fields: {len(result['required_fields'])}")
print(f"Optional fields: {len(result['optional_fields'])}")
```

**Sample Output:**
```json
{
  "job_title": "Senior Software Engineer",
  "company_name": "TechCorp",
  "required_fields": [
    {
      "field_name": "First Name",
      "field_type": "text",
      "locator_type": "id",
      "locator_value": "firstName",
      "is_required": true,
      "placeholder_text": "Enter your first name"
    }
  ],
  "optional_fields": [...],
  "file_upload_fields": [...],
  "extraction_status": "success"
}
```

### Tool 2: Form Filling

```python
from toolCalling3 import fill_job_application_form
import json

# Use extracted field data to fill the form
field_data_json = json.dumps(extraction_result)

filling_result = fill_job_application_form.invoke({
    "field_data": field_data_json
})

print(f"Status: {filling_result['filling_status']}")
print(f"Success rate: {filling_result['success_rate']}%")
```

**Sample Output:**
```json
{
  "filling_status": "success",
  "filled_fields": ["First Name", "Last Name", "Email", "Phone"],
  "failed_fields": [],
  "screenshot_path": "screenshots/filled_form_20231201_143022.png",
  "total_fields": 4,
  "success_rate": 100.0
}
```

### Complete Workflow

```python
from toolCalling3 import demo_job_application_automation

# Run the complete demo
demo_job_application_automation()
```

## Configuration

### Custom Profile Data

You can provide custom profile data for form filling:

```python
custom_profile = {
    "personal_info": {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@email.com",
        "phone": "+1-555-987-6543"
    },
    # ... more fields
}

result = fill_job_application_form.invoke({
    "field_data": field_data_json,
    "profile_data": json.dumps(custom_profile)
})
```

### Default Profile Structure

```json
{
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
  "cover_letter": "I am excited to apply for this position...",
  "additional_info": "I am passionate about building scalable applications..."
}
```

## Advanced Features

### Multiple Element Location Strategies

The tools implement multiple fallback strategies for finding form elements:

1. **Primary Strategy**: Uses LLM-extracted locators (ID, name, CSS selector, XPath)
2. **Fallback Strategies**: Tries common naming patterns and element attributes
3. **Smart Matching**: Uses fuzzy matching for field names and labels

### Human-like Interactions

- **Typing Simulation**: Random delays between keystrokes (50-100ms)
- **Scroll Behavior**: Automatically scrolls elements into view
- **Wait Times**: Realistic pauses between field interactions
- **Element Visibility**: Waits for elements to be interactive before filling

### Error Recovery

- **Retry Logic**: Multiple attempts to locate elements
- **Graceful Degradation**: Continues with remaining fields if some fail
- **Detailed Logging**: Comprehensive error reporting with stack traces
- **Screenshot Capture**: Takes screenshots on errors for debugging

## API Reference

### extract_job_application_fields_with_locators

**Parameters:**
- `url` (str): Ashby job application URL

**Returns:**
- `dict`: Structured data containing job info, fields, and locators

**Key Output Fields:**
- `job_title`: Position title
- `company_name`: Company name
- `required_fields`: List of required form fields with locators
- `optional_fields`: List of optional form fields with locators
- `file_upload_fields`: File upload requirements
- `extraction_status`: "success" or "error"

### fill_job_application_form

**Parameters:**
- `field_data` (str): JSON string from field extraction tool
- `profile_data` (str, optional): JSON string with custom profile data

**Returns:**
- `dict`: Form filling results and statistics

**Key Output Fields:**
- `filling_status`: "success", "partial", or "error"
- `filled_fields`: List of successfully filled field names
- `failed_fields`: List of failed fields with error reasons
- `screenshot_path`: Path to screenshot of filled form
- `success_rate`: Percentage of successfully filled fields

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   ```bash
   # Install ChromeDriver manually
   pip install webdriver-manager
   ```

2. **OpenAI API Errors**
   - Verify your API key is set correctly
   - Check your OpenAI account has available credits

3. **Element Not Found**
   - Website structure may have changed
   - Try running with updated Ashby URLs
   - Check browser console for JavaScript errors

4. **Permission Errors**
   ```bash
   # On macOS, you may need to allow Chrome automation
   # Go to System Preferences > Security & Privacy > Privacy > Automation
   ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Screenshots

Screenshots are automatically saved to the `screenshots/` directory with timestamps:
- `initial_form_YYYYMMDD_HHMMSS.png`: Before filling
- `filled_form_YYYYMMDD_HHMMSS.png`: After filling
- `error_form_YYYYMMDD_HHMMSS.png`: On errors

## Known Limitations

1. **Ashby-Specific**: Designed specifically for Ashby job application pages
2. **File Uploads**: Does not handle actual file uploads (resume, cover letter)
3. **CAPTCHA**: Cannot solve CAPTCHA challenges
4. **Dynamic Forms**: May struggle with heavily dynamic forms that change structure
5. **Rate Limiting**: No built-in rate limiting for multiple applications

## Future Enhancements

- [ ] Support for other job application platforms (Greenhouse, Lever, etc.)
- [ ] File upload handling with sample documents
- [ ] CAPTCHA detection and notification
- [ ] Batch processing for multiple applications
- [ ] Integration with job search APIs
- [ ] Chrome extension for manual triggering
- [ ] Database storage for application tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. Always respect website terms of service and rate limits. The authors are not responsible for any misuse of this software. 