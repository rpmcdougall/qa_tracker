#!/usr/bin/env python3
"""
Test script to validate the two-phase QA implementation
"""

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from models import (
            Database, QAList, QAItem, QAValidation,
            QASession, QATemplate, QASessionPhase2Item
        )
        print("✓ All model classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database_init():
    """Test database initialization"""
    print("\nTesting database initialization...")
    try:
        from models import Database
        db = Database()
        print("✓ Database initialized successfully")
        print("✓ Tables created: qa_lists, qa_items, qa_validations, qa_sessions,")
        print("  qa_templates, qa_template_items, qa_session_phase2_items")
        return True
    except Exception as e:
        print(f"✗ Database initialization error: {e}")
        return False

def test_create_sample_data():
    """Create sample data for testing"""
    print("\nCreating sample data...")
    try:
        from models import Database, QAList, QAItem, QASession, QATemplate

        db = Database()
        qa_list_model = QAList(db)
        qa_item_model = QAItem(db)
        qa_session_model = QASession(db)
        qa_template_model = QATemplate(db)

        # Create a QA list
        list_id = qa_list_model.create("Test Feature QA", "Testing the new login feature")
        print(f"✓ Created QA list (ID: {list_id})")

        # Add items to the list
        item1_id = qa_item_model.create(
            list_id,
            "Test login with valid credentials",
            category="Functionality",
            expected_result="User successfully logs in"
        )
        item2_id = qa_item_model.create(
            list_id,
            "Test login with invalid credentials",
            category="Security",
            expected_result="Error message displayed"
        )
        print(f"✓ Created 2 QA items (IDs: {item1_id}, {item2_id})")

        # Publish the list
        qa_list_model.publish(list_id)
        print("✓ Published QA list")

        # Create a template
        template_id = qa_template_model.create(
            "Security Checks",
            "Standard security validation items",
            "Security"
        )
        qa_template_model.add_item(
            template_id,
            "Test for SQL injection vulnerabilities",
            category="Security",
            expected_result="No SQL injection possible"
        )
        print(f"✓ Created QA template (ID: {template_id})")

        # Create a session
        session_id = qa_session_model.create(list_id, "Sprint 23 QA Session")
        print(f"✓ Created QA session (ID: {session_id})")

        return True
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow():
    """Test the two-phase workflow"""
    print("\nTesting two-phase workflow...")
    try:
        from models import Database, QAValidation, QASession, QASessionPhase2Item

        db = Database()
        qa_session_model = QASession(db)
        qa_validation_model = QAValidation(db)
        qa_phase2_item_model = QASessionPhase2Item(db)

        # Get the session we created
        sessions = qa_session_model.get_by_list(1)
        if not sessions:
            print("✗ No sessions found")
            return False

        session = sessions[0]
        session_id = session['id']

        print(f"Testing with session ID: {session_id}")

        # Test Phase 1 validation
        validation_id = qa_validation_model.create(
            session_id=session_id,
            phase=1,
            list_id=1,
            item_id=1,
            status='pass',
            actual_result='Login successful',
            validator_name='Developer John'
        )
        print(f"✓ Created Phase 1 validation (ID: {validation_id})")

        # Complete Phase 1
        try:
            # This will fail because not all items are validated
            qa_session_model.complete_phase1(session_id, 'Developer John')
            print("✗ Phase 1 completion should have failed (not all items validated)")
            return False
        except ValueError as e:
            print(f"✓ Phase 1 completion correctly rejected: {e}")

        # Validate the second item
        validation_id2 = qa_validation_model.create(
            session_id=session_id,
            phase=1,
            list_id=1,
            item_id=2,
            status='pass',
            validator_name='Developer John'
        )
        print(f"✓ Created second Phase 1 validation (ID: {validation_id2})")

        # Now complete Phase 1
        qa_session_model.complete_phase1(session_id, 'Developer John')
        print("✓ Phase 1 completed successfully")

        # Start Phase 2
        qa_session_model.start_phase2(session_id)
        print("✓ Phase 2 started successfully")

        # Add a Phase 2 custom item
        phase2_item_id = qa_phase2_item_model.add_manual_item(
            session_id,
            "Test logout functionality",
            category="Functionality",
            expected_result="User successfully logs out"
        )
        print(f"✓ Added Phase 2 custom item (ID: {phase2_item_id})")

        # Create Phase 2 validation
        phase2_validation_id = qa_validation_model.create(
            session_id=session_id,
            phase=2,
            list_id=1,
            item_id=1,  # Validating original item in Phase 2
            status='pass',
            validator_name='QA Engineer Sarah'
        )
        print(f"✓ Created Phase 2 validation for original item (ID: {phase2_validation_id})")

        # Test getting validations by phase
        phase1_validations = qa_validation_model.get_by_session(session_id, phase=1)
        phase2_validations = qa_validation_model.get_by_session(session_id, phase=2)
        print(f"✓ Retrieved validations: Phase 1={len(phase1_validations)}, Phase 2={len(phase2_validations)}")

        # Test timeline
        timeline = qa_validation_model.get_timeline(session_id)
        print(f"✓ Retrieved timeline: {len(timeline)} total validations")

        # Test summaries
        summary_p1 = qa_validation_model.get_summary(session_id=session_id, phase=1)
        summary_p2 = qa_validation_model.get_summary(session_id=session_id, phase=2)
        print(f"✓ Phase 1 summary: {summary_p1}")
        print(f"✓ Phase 2 summary: {summary_p2}")

        return True
    except Exception as e:
        print(f"✗ Workflow test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Two-Phase QA Implementation Test")
    print("=" * 60)

    all_passed = True

    if not test_imports():
        print("\n⚠ Please install dependencies first:")
        print("  pip install -r requirements.txt")
        exit(1)

    all_passed = test_database_init() and all_passed
    all_passed = test_create_sample_data() and all_passed
    all_passed = test_workflow() and all_passed

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nYou can now run the application:")
        print("  python3 app.py")
        print("\nThen visit: http://localhost:5000")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the errors above.")
    print("=" * 60)
