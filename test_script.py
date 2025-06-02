#!/usr/bin/env python3
"""
Test script demonstrating the job application automation tools.

This script tests both tools:
1. extract_job_application_fields_with_locators
2. fill_job_application_form

Usage:
    python test_script.py [URL]

If no URL is provided, uses the default Wander job posting.
"""

import sys
import json
import time
from pathlib import Path
from toolCalling3 import (
    extract_job_application_fields_with_locators,
    fill_job_application_form,
    DUMMY_PROFILE
)

def print_separator(title=""):
    """Print a formatted separator"""
    print("\n" + "="*80)
    if title:
        print(f" {title} ".center(80, "="))
        print("="*80)
    print()

def print_field_details(fields, field_type_name):
    """Print detailed information about form fields"""
    if not fields:
        print(f"No {field_type_name.lower()} found.")
        return
    
    print(f"{field_type_name} ({len(fields)} total):")
    for i, field in enumerate(fields, 1):
        print(f"  {i}. {field['field_name']}")
        print(f"     Type: {field['field_type']}")
        print(f"     Locator: {field['locator_type']} = '{field['locator_value']}'")
        print(f"     Required: {field['is_required']}")
        if field.get('placeholder_text'):
            print(f"     Placeholder: {field['placeholder_text']}")
        print()

def test_field_extraction(url):
    """Test the field extraction tool"""
    print_separator("TESTING FIELD EXTRACTION")
    
    print(f"🔍 Extracting fields from: {url}")
    print("⏳ This may take 10-15 seconds...")
    
    start_time = time.time()
    result = extract_job_application_fields_with_locators.invoke({"url": url})
    extraction_time = time.time() - start_time
    
    print(f"⏱️  Extraction completed in {extraction_time:.1f} seconds")
    
    if result["extraction_status"] == "success":
        print("✅ Field extraction SUCCESSFUL!")
        print()
        print(f"🏢 Company: {result['company_name']}")
        print(f"💼 Job Title: {result['job_title']}")
        print(f"🔗 URL: {result['url']}")
        print(f"📊 Total Fields: {result['total_fields']}")
        print()
        
        # Print detailed field information
        print_field_details(result['required_fields'], "Required Fields")
        print_field_details(result['optional_fields'], "Optional Fields")
        
        if result['file_upload_fields']:
            print(f"📁 File Upload Fields ({len(result['file_upload_fields'])} total):")
            for i, upload in enumerate(result['file_upload_fields'], 1):
                print(f"  {i}. {upload['field_name']}")
                print(f"     Locator: {upload['locator_type']} = '{upload['locator_value']}'")
                print(f"     Required: {upload['is_required']}")
                if upload.get('accepted_formats'):
                    print(f"     Formats: {', '.join(upload['accepted_formats'])}")
                print()
        
        if result['dropdown_options']:
            print(f"📋 Dropdown Options ({len(result['dropdown_options'])} total):")
            for dropdown in result['dropdown_options']:
                print(f"  {dropdown}")
            print()
        
        return result
    else:
        print("❌ Field extraction FAILED!")
        print(f"Error Type: {result.get('error_type', 'Unknown')}")
        print(f"Error Message: {result.get('error_message', 'No error message')}")
        if result.get('full_traceback'):
            print(f"Full Traceback:\n{result['full_traceback']}")
        return None

def test_form_filling(field_data):
    """Test the form filling tool"""
    print_separator("TESTING FORM FILLING")
    
    if not field_data:
        print("❌ Cannot test form filling - no field data available")
        return None
    
    print("🤖 Starting automated form filling...")
    print("📋 Using dummy profile data:")
    print(f"   Name: {DUMMY_PROFILE['personal_info']['first_name']} {DUMMY_PROFILE['personal_info']['last_name']}")
    print(f"   Email: {DUMMY_PROFILE['personal_info']['email']}")
    print(f"   Phone: {DUMMY_PROFILE['personal_info']['phone']}")
    print(f"   Location: {DUMMY_PROFILE['address']['city']}, {DUMMY_PROFILE['address']['state']}")
    print()
    
    print("⚠️  Browser will open in NON-HEADLESS mode - you'll see the form being filled!")
    print("⏳ This may take 30-60 seconds...")
    
    # Convert field data to JSON string
    field_data_json = json.dumps(field_data)
    
    start_time = time.time()
    result = fill_job_application_form.invoke({"field_data": field_data_json})
    filling_time = time.time() - start_time
    
    print(f"⏱️  Form filling completed in {filling_time:.1f} seconds")
    
    # Print results
    status_icon = {
        "success": "✅",
        "partial": "⚠️",
        "error": "❌"
    }.get(result['filling_status'], "❓")
    
    print(f"{status_icon} Form filling status: {result['filling_status'].upper()}")
    print()
    
    print("📊 FILLING STATISTICS:")
    print(f"   Total fields: {result['total_fields']}")
    print(f"   Successfully filled: {len(result['filled_fields'])}")
    print(f"   Failed to fill: {len(result['failed_fields'])}")
    print(f"   Success rate: {result['success_rate']}%")
    print()
    
    if result['filled_fields']:
        print("✅ SUCCESSFULLY FILLED FIELDS:")
        for i, field in enumerate(result['filled_fields'], 1):
            print(f"   {i}. {field}")
        print()
    
    if result['failed_fields']:
        print("❌ FAILED FIELDS:")
        for i, failed in enumerate(result['failed_fields'], 1):
            print(f"   {i}. {failed['field_name']}")
            print(f"      Error: {failed['error']}")
        print()
    
    if result['screenshot_path']:
        screenshot_path = Path(result['screenshot_path'])
        if screenshot_path.exists():
            print(f"📸 Screenshot saved: {result['screenshot_path']}")
            print(f"   File size: {screenshot_path.stat().st_size:,} bytes")
        else:
            print(f"⚠️  Screenshot path provided but file not found: {result['screenshot_path']}")
    
    if result.get('error_message'):
        print(f"❌ Error during filling: {result['error_message']}")
    
    return result

def save_results_to_file(extraction_result, filling_result, url):
    """Save test results to a JSON file"""
    results = {
        "test_metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "extraction_time": time.time(),
            "filling_time": time.time()
        },
        "extraction_result": extraction_result,
        "filling_result": filling_result
    }
    
    # Create results directory if it doesn't exist
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    # Save with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"test_results/automation_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Test results saved to: {filename}")
    return filename

def main():
    """Main test function"""
    # Get URL from command line argument or use default
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://jobs.ashbyhq.com/wander/121c24e0-eeff-49a8-ac56-793d2dbc9fcd/application"
        print(f"🔗 No URL provided, using default: {test_url}")
    
    print_separator("JOB APPLICATION AUTOMATION TEST SUITE")
    print(f"🎯 Target URL: {test_url}")
    print(f"🕐 Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Field Extraction
    extraction_result = test_field_extraction(test_url)
    
    # Test 2: Form Filling (only if extraction succeeded)
    filling_result = None
    if extraction_result and extraction_result["extraction_status"] == "success":
        filling_result = test_form_filling(extraction_result)
    else:
        print_separator("SKIPPING FORM FILLING")
        print("❌ Skipping form filling test due to extraction failure")
    
    # Save results
    print_separator("SAVING RESULTS")
    if extraction_result:
        results_file = save_results_to_file(extraction_result, filling_result, test_url)
    
    # Final summary
    print_separator("TEST SUMMARY")
    
    if extraction_result and extraction_result["extraction_status"] == "success":
        print("✅ Field extraction: PASSED")
    else:
        print("❌ Field extraction: FAILED")
    
    if filling_result:
        if filling_result["filling_status"] == "success":
            print("✅ Form filling: PASSED")
        elif filling_result["filling_status"] == "partial":
            print("⚠️  Form filling: PARTIAL SUCCESS")
        else:
            print("❌ Form filling: FAILED")
    else:
        print("⏭️  Form filling: SKIPPED")
    
    print(f"🕐 Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code based on results
    if extraction_result and extraction_result["extraction_status"] == "success":
        if not filling_result or filling_result["filling_status"] in ["success", "partial"]:
            print("\n🎉 Overall test result: SUCCESS")
            return 0
    
    print("\n💥 Overall test result: FAILURE")
    return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 