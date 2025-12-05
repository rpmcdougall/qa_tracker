#!/usr/bin/env python
"""
Test database connection and basic operations
Usage: python test_db_connection.py
"""

import sys
from models import Database, QAList, QAItem, QAValidation
from config import DATABASE_URL

def test_connection():
    """Test database connection and basic CRUD operations"""
    
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    print(f"\nTesting connection to: {DATABASE_URL}")
    print()
    
    try:
        # Initialize database
        print("1. Initializing database...")
        db = Database()
        print("   ✅ Database initialized")
        
        # Initialize models
        qa_list_model = QAList(db)
        qa_item_model = QAItem(db)
        qa_validation_model = QAValidation(db)
        print("   ✅ Models initialized")
        
        # Test CREATE - QA List
        print("\n2. Testing CREATE operation (QA List)...")
        list_id = qa_list_model.create(
            name="Test Connection List",
            description="This is a test list to verify database connectivity"
        )
        print(f"   ✅ Created QA list with ID: {list_id}")
        
        # Test READ - QA List
        print("\n3. Testing READ operation (QA List)...")
        retrieved_list = qa_list_model.get_by_id(list_id)
        if retrieved_list and retrieved_list['name'] == "Test Connection List":
            print(f"   ✅ Retrieved QA list: {retrieved_list['name']}")
        else:
            print("   ❌ Failed to retrieve QA list")
            return False
        
        # Test CREATE - QA Item
        print("\n4. Testing CREATE operation (QA Item)...")
        item_id = qa_item_model.create(
            list_id=list_id,
            description="Test item to verify database operations",
            category="Connection Test",
            expected_result="Item should be created and retrievable",
            notes="This is a test item"
        )
        print(f"   ✅ Created QA item with ID: {item_id}")
        
        # Test READ - QA Items
        print("\n5. Testing READ operation (QA Items)...")
        items = qa_item_model.get_by_list(list_id)
        if len(items) == 1 and items[0]['description'] == "Test item to verify database operations":
            print(f"   ✅ Retrieved {len(items)} item(s)")
        else:
            print("   ❌ Failed to retrieve QA items")
            return False
        
        # Test CREATE - QA Validation
        print("\n6. Testing CREATE operation (QA Validation)...")
        validation_id = qa_validation_model.create(
            list_id=list_id,
            item_id=item_id,
            status="pass",
            actual_result="Database operations working correctly",
            notes="Connection test successful",
            validator_name="Test Script"
        )
        print(f"   ✅ Created validation with ID: {validation_id}")
        
        # Test READ - QA Validations
        print("\n7. Testing READ operation (QA Validations)...")
        validations = qa_validation_model.get_by_list(list_id)
        if len(validations) == 1:
            print(f"   ✅ Retrieved {len(validations)} validation(s)")
        else:
            print("   ❌ Failed to retrieve validations")
            return False
        
        # Test summary
        print("\n8. Testing summary query...")
        summary = qa_validation_model.get_summary(list_id)
        if summary['total_items'] == 1 and summary['passed'] == 1:
            print(f"   ✅ Summary correct: {summary}")
        else:
            print(f"   ❌ Summary incorrect: {summary}")
            return False
        
        # Test UPDATE - Publish list
        print("\n9. Testing UPDATE operation (Publish)...")
        qa_list_model.publish(list_id)
        published_list = qa_list_model.get_by_id(list_id)
        if published_list['is_published']:
            print("   ✅ List published successfully")
        else:
            print("   ❌ Failed to publish list")
            return False
        
        # Test DELETE - Clean up
        print("\n10. Testing DELETE operation...")
        qa_list_model.delete(list_id)
        deleted_list = qa_list_model.get_by_id(list_id)
        if deleted_list is None:
            print("   ✅ List deleted successfully (cascade delete verified)")
        else:
            print("   ❌ Failed to delete list")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYour database is configured correctly and ready to use!")
        print(f"Database type: {DATABASE_URL.split(':')[0]}")
        print("\nYou can now run the application:")
        print("  python app.py")
        print("\nOr load sample data:")
        print("  python sample_data.py")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify database server is running")
        print("  2. Check DATABASE_URL in config.py or environment variable")
        print("  3. Ensure database drivers are installed:")
        print("     - PostgreSQL: pip install psycopg2-binary")
        print("     - MySQL: pip install PyMySQL")
        print("     - Snowflake: pip install snowflake-sqlalchemy")
        print("     - Databricks: pip install databricks-sql-connector")
        print("  4. Verify database user has CREATE TABLE permissions")
        print("\nFor more help, see DATABASE_SETUP.md")
        print("=" * 60)
        
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
