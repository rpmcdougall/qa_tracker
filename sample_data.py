"""
Sample data script to populate the QA Tracker with example lists and items.
Run this after starting the app for the first time to see how it works.

Usage: python sample_data.py
"""

from models import Database, QAList, QAItem, QAValidation

def create_sample_data():
    """Create sample QA lists and items"""
    
    # Initialize database
    db = Database()
    qa_list_model = QAList(db)
    qa_item_model = QAItem(db)
    qa_validation_model = QAValidation(db)
    
    print("Creating sample QA lists...")
    
    # List 1: ETL Pipeline QA
    list1_id = qa_list_model.create(
        name="Customer Data ETL Pipeline QA",
        description="Validation checklist for the daily customer data ETL process from Oracle to Databricks"
    )
    
    # Add items to List 1
    items1 = [
        {
            "category": "Data Extraction",
            "description": "Verify source database connection and data extraction",
            "expected_result": "Successfully connect to Oracle source and extract customer records from past 24 hours",
            "notes": "Check Databricks notebook logs. Expected row count should be 5000-8000 based on historical averages"
        },
        {
            "category": "Data Transformation",
            "description": "Validate phone number formatting transformation",
            "expected_result": "All phone numbers converted to (XXX) XXX-XXXX format",
            "notes": "Sample check first 100 records. Original format varies: XXX-XXX-XXXX, XXXXXXXXXX, etc."
        },
        {
            "category": "Data Transformation",
            "description": "Verify email address standardization",
            "expected_result": "All email addresses converted to lowercase and validated for proper format",
            "notes": "Check for null values and invalid formats. Should reject emails without @ symbol"
        },
        {
            "category": "Data Quality",
            "description": "Check for duplicate customer IDs",
            "expected_result": "Zero duplicate customer_id values in transformed dataset",
            "notes": "SQL: SELECT customer_id, COUNT(*) FROM customers GROUP BY customer_id HAVING COUNT(*) > 1"
        },
        {
            "category": "Data Quality",
            "description": "Validate mandatory field completeness",
            "expected_result": "No null values in required fields: customer_id, first_name, last_name, email",
            "notes": "Check each required field separately and report counts"
        },
        {
            "category": "Data Load",
            "description": "Confirm successful load to target table",
            "expected_result": "Row count in target table matches transformed dataset count",
            "notes": "Compare counts: source extraction = transformation output = target load"
        },
        {
            "category": "Performance",
            "description": "Verify pipeline completion time",
            "expected_result": "Total pipeline execution time under 30 minutes",
            "notes": "Check Databricks job runtime. SLA is 30 minutes for daily batch"
        }
    ]
    
    for item in items1:
        qa_item_model.create(list1_id, **item)
    
    # Publish List 1
    qa_list_model.publish(list1_id)
    print(f"✓ Created '{qa_list_model.get_by_id(list1_id)['name']}' with {len(items1)} items (published)")
    
    # Add some sample validations to show results
    validations1 = [
        {"item_id": 1, "status": "pass", "actual_result": "Successfully extracted 6,234 records", "validator_name": "Ryan"},
        {"item_id": 2, "status": "pass", "actual_result": "All phone numbers properly formatted", "validator_name": "Ryan"},
        {"item_id": 3, "status": "pass", "actual_result": "Email standardization working correctly", "validator_name": "Ryan"},
        {"item_id": 4, "status": "fail", "actual_result": "Found 3 duplicate customer IDs", 
         "notes": "IDs: 12345, 67890, 11223 - Opened ticket JIRA-1234", "validator_name": "Ryan"},
        {"item_id": 5, "status": "pass", "actual_result": "All mandatory fields complete", "validator_name": "Ryan"}
    ]
    
    for val in validations1:
        qa_validation_model.create(list1_id, **val)
    
    # List 2: Web Application Feature QA
    list2_id = qa_list_model.create(
        name="User Registration Feature QA",
        description="Quality assurance checklist for the new user registration flow with email verification"
    )
    
    items2 = [
        {
            "category": "Functionality",
            "description": "Verify user can access registration page",
            "expected_result": "Registration page loads without errors, all form fields visible",
            "notes": "Test in Chrome, Firefox, and Safari"
        },
        {
            "category": "Functionality",
            "description": "Test successful registration with valid data",
            "expected_result": "User account created, verification email sent, redirected to confirmation page",
            "notes": "Use test data: john.doe@example.com, password: Test123!"
        },
        {
            "category": "Validation",
            "description": "Test email format validation",
            "expected_result": "Form rejects invalid email formats with clear error message",
            "notes": "Test cases: missing @, no domain, spaces in email"
        },
        {
            "category": "Validation",
            "description": "Test password strength requirements",
            "expected_result": "Password must have 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 special char",
            "notes": "Error message should specify which requirement failed"
        },
        {
            "category": "Security",
            "description": "Verify password is not visible in clear text",
            "expected_result": "Password field shows bullets/asterisks, not actual characters",
            "notes": "Check with browser dev tools that password is masked"
        },
        {
            "category": "UI/UX",
            "description": "Test form responsiveness on mobile devices",
            "expected_result": "Form is usable and properly formatted on screens 320px to 768px wide",
            "notes": "Test with Chrome DevTools mobile emulation"
        },
        {
            "category": "Integration",
            "description": "Verify email verification link works",
            "expected_result": "Clicking verification link activates account and allows login",
            "notes": "Check email arrives within 1 minute of registration"
        }
    ]
    
    for item in items2:
        qa_item_model.create(list2_id, **item)
    
    qa_list_model.publish(list2_id)
    print(f"✓ Created '{qa_list_model.get_by_id(list2_id)['name']}' with {len(items2)} items (published)")
    
    # List 3: SQL Query Optimization QA (unpublished draft)
    list3_id = qa_list_model.create(
        name="SQL Query Performance Optimization QA",
        description="Checklist for validating optimized CTE queries for customer analytics dashboard"
    )
    
    items3 = [
        {
            "category": "Performance",
            "description": "Compare execution time: original vs optimized query",
            "expected_result": "Optimized query runs in under 5 seconds (vs 45 seconds original)",
            "notes": "Run EXPLAIN ANALYZE on both queries. Test with production-size dataset (10M rows)"
        },
        {
            "category": "Accuracy",
            "description": "Verify query results match original output",
            "expected_result": "100% match in row count and values between original and optimized queries",
            "notes": "Use EXCEPT to find differences. Sample 1000 random rows for detailed comparison"
        },
        {
            "category": "Index Usage",
            "description": "Confirm proper index utilization",
            "expected_result": "Query plan shows index scans instead of full table scans",
            "notes": "Check EXPLAIN output. Should use customer_id_idx and created_date_idx"
        },
        {
            "category": "Edge Cases",
            "description": "Test with empty result set",
            "expected_result": "Query handles no matching records gracefully without errors",
            "notes": "Use WHERE clause that matches zero records"
        },
        {
            "category": "Edge Cases",
            "description": "Test with NULL values in key fields",
            "expected_result": "Query properly handles NULL values per business logic",
            "notes": "Insert test records with NULL in customer_name and purchase_date"
        }
    ]
    
    for item in items3:
        qa_item_model.create(list3_id, **item)
    
    # This list is NOT published - it's a draft
    print(f"✓ Created '{qa_list_model.get_by_id(list3_id)['name']}' with {len(items3)} items (draft)")
    
    print("\n✓ Sample data created successfully!")
    print(f"\nCreated {3} QA lists with a total of {len(items1) + len(items2) + len(items3)} items")
    print("Start the Flask app (python app.py) and visit http://localhost:5000 to see the data")

if __name__ == "__main__":
    create_sample_data()
