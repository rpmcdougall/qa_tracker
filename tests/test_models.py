#!/usr/bin/env python3
"""
Comprehensive unit tests for database models and service classes
"""

import unittest
import os
import tempfile
from datetime import datetime
from models import (
    Database, QAList, QAItem, QAValidation, QASession,
    QATemplate, QASessionPhase2Item
)


class TestDatabase(unittest.TestCase):
    """Test Database class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_database_initialization(self):
        """Test database initialization"""
        self.assertIsNotNone(self.db)
        session = self.db.get_session()
        self.assertIsNotNone(session)
        session.close()


class TestQAListModel(unittest.TestCase):
    """Test QAList service class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_list = QAList(self.db)

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_list(self):
        """Test creating a QA list"""
        list_id = self.qa_list.create("Test List", "Test Description")
        self.assertIsNotNone(list_id)
        self.assertIsInstance(list_id, int)

    def test_create_list_without_description(self):
        """Test creating a list without description"""
        list_id = self.qa_list.create("Test List")
        self.assertIsNotNone(list_id)

    def test_get_list_by_id(self):
        """Test retrieving a list by ID"""
        list_id = self.qa_list.create("Test List", "Description")
        retrieved = self.qa_list.get_by_id(list_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['id'], list_id)
        self.assertEqual(retrieved['name'], "Test List")
        self.assertEqual(retrieved['description'], "Description")
        self.assertFalse(retrieved['is_published'])

    def test_get_nonexistent_list(self):
        """Test retrieving a nonexistent list"""
        result = self.qa_list.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_all_lists(self):
        """Test retrieving all lists"""
        self.qa_list.create("List 1")
        self.qa_list.create("List 2")

        all_lists = self.qa_list.get_all()
        self.assertEqual(len(all_lists), 2)

    def test_get_published_lists_only(self):
        """Test retrieving only published lists"""
        list_id1 = self.qa_list.create("Published List")
        list_id2 = self.qa_list.create("Unpublished List")

        self.qa_list.publish(list_id1)

        published = self.qa_list.get_all(published_only=True)
        self.assertEqual(len(published), 1)
        self.assertEqual(published[0]['name'], "Published List")

    def test_publish_list(self):
        """Test publishing a list"""
        list_id = self.qa_list.create("Test List")
        self.qa_list.publish(list_id)

        retrieved = self.qa_list.get_by_id(list_id)
        self.assertTrue(retrieved['is_published'])

    def test_unpublish_list(self):
        """Test unpublishing a list"""
        list_id = self.qa_list.create("Test List")
        self.qa_list.publish(list_id)
        self.qa_list.unpublish(list_id)

        retrieved = self.qa_list.get_by_id(list_id)
        self.assertFalse(retrieved['is_published'])

    def test_delete_list(self):
        """Test deleting a list"""
        list_id = self.qa_list.create("Test List")
        self.qa_list.delete(list_id)

        result = self.qa_list.get_by_id(list_id)
        self.assertIsNone(result)


class TestQAItemModel(unittest.TestCase):
    """Test QAItem service class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_list = QAList(self.db)
        self.qa_item = QAItem(self.db)
        self.list_id = self.qa_list.create("Test List")

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_item(self):
        """Test creating a QA item"""
        item_id = self.qa_item.create(
            self.list_id,
            "Test Description",
            category="Functionality",
            expected_result="Should work",
            notes="Test notes"
        )
        self.assertIsNotNone(item_id)

    def test_create_item_minimal(self):
        """Test creating an item with minimal fields"""
        item_id = self.qa_item.create(self.list_id, "Test Description")
        self.assertIsNotNone(item_id)

    def test_item_auto_ordering(self):
        """Test automatic item ordering"""
        item1 = self.qa_item.create(self.list_id, "Item 1")
        item2 = self.qa_item.create(self.list_id, "Item 2")
        item3 = self.qa_item.create(self.list_id, "Item 3")

        items = self.qa_item.get_by_list(self.list_id)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['item_order'], 1)
        self.assertEqual(items[1]['item_order'], 2)
        self.assertEqual(items[2]['item_order'], 3)

    def test_get_items_by_list(self):
        """Test retrieving items for a list"""
        self.qa_item.create(self.list_id, "Item 1")
        self.qa_item.create(self.list_id, "Item 2")

        items = self.qa_item.get_by_list(self.list_id)
        self.assertEqual(len(items), 2)

    def test_update_item(self):
        """Test updating an item"""
        item_id = self.qa_item.create(self.list_id, "Original")
        self.qa_item.update(item_id, description="Updated", category="Security")

        items = self.qa_item.get_by_list(self.list_id)
        self.assertEqual(items[0]['description'], "Updated")
        self.assertEqual(items[0]['category'], "Security")

    def test_delete_item(self):
        """Test deleting an item"""
        item_id = self.qa_item.create(self.list_id, "To Delete")
        self.qa_item.delete(item_id)

        items = self.qa_item.get_by_list(self.list_id)
        self.assertEqual(len(items), 0)


class TestQASessionModel(unittest.TestCase):
    """Test QASession service class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_list = QAList(self.db)
        self.qa_item = QAItem(self.db)
        self.qa_session = QASession(self.db)
        self.qa_validation = QAValidation(self.db)

        self.list_id = self.qa_list.create("Test List")
        self.item1_id = self.qa_item.create(self.list_id, "Item 1")
        self.item2_id = self.qa_item.create(self.list_id, "Item 2")

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_session(self):
        """Test creating a session"""
        session_id = self.qa_session.create(self.list_id, "Test Session")
        self.assertIsNotNone(session_id)

    def test_session_initial_phase(self):
        """Test session starts in Phase 1"""
        session_id = self.qa_session.create(self.list_id, "Test Session")
        session = self.qa_session.get_by_id(session_id)

        self.assertEqual(session['current_phase'], 1)
        self.assertIsNotNone(session['phase1_started_at'])
        self.assertIsNone(session['phase1_completed_at'])

    def test_get_session_by_id(self):
        """Test retrieving session by ID"""
        session_id = self.qa_session.create(self.list_id, "Test Session")
        session = self.qa_session.get_by_id(session_id)

        self.assertEqual(session['id'], session_id)
        self.assertEqual(session['session_name'], "Test Session")

    def test_get_sessions_by_list(self):
        """Test retrieving sessions for a list"""
        self.qa_session.create(self.list_id, "Session 1")
        self.qa_session.create(self.list_id, "Session 2")

        sessions = self.qa_session.get_by_list(self.list_id)
        self.assertEqual(len(sessions), 2)

    def test_complete_phase1_requires_validations(self):
        """Test Phase 1 completion requires all items validated"""
        session_id = self.qa_session.create(self.list_id, "Test Session")

        # Try to complete without validations - should fail
        with self.assertRaises(ValueError):
            self.qa_session.complete_phase1(session_id, "Developer")

    def test_complete_phase1_success(self):
        """Test successful Phase 1 completion"""
        session_id = self.qa_session.create(self.list_id, "Test Session")

        # Validate all items
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=self.list_id,
            item_id=self.item1_id, status='pass'
        )
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=self.list_id,
            item_id=self.item2_id, status='pass'
        )

        # Complete Phase 1
        self.qa_session.complete_phase1(session_id, "Developer")

        session = self.qa_session.get_by_id(session_id)
        self.assertIsNotNone(session['phase1_completed_at'])
        self.assertEqual(session['phase1_completed_by'], "Developer")

    def test_start_phase2_requires_phase1_complete(self):
        """Test Phase 2 start requires Phase 1 completion"""
        session_id = self.qa_session.create(self.list_id, "Test Session")

        with self.assertRaises(ValueError):
            self.qa_session.start_phase2(session_id)

    def test_start_phase2_success(self):
        """Test successful Phase 2 start"""
        session_id = self.qa_session.create(self.list_id, "Test Session")

        # Complete Phase 1
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=self.list_id,
            item_id=self.item1_id, status='pass'
        )
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=self.list_id,
            item_id=self.item2_id, status='pass'
        )
        self.qa_session.complete_phase1(session_id, "Developer")

        # Start Phase 2
        result = self.qa_session.start_phase2(session_id)

        self.assertTrue(result)
        session = self.qa_session.get_by_id(session_id)
        self.assertEqual(session['current_phase'], 2)
        self.assertIsNotNone(session['phase2_started_at'])

    def test_complete_phase2(self):
        """Test Phase 2 completion"""
        session_id = self.qa_session.create(self.list_id, "Test Session")

        # Complete Phase 1
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=self.list_id,
            item_id=self.item1_id, status='pass'
        )
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=self.list_id,
            item_id=self.item2_id, status='pass'
        )
        self.qa_session.complete_phase1(session_id, "Developer")
        self.qa_session.start_phase2(session_id)

        # Complete Phase 2
        self.qa_session.complete_phase2(session_id, "QA Engineer")

        session = self.qa_session.get_by_id(session_id)
        self.assertIsNotNone(session['phase2_completed_at'])
        self.assertEqual(session['phase2_completed_by'], "QA Engineer")
        self.assertIsNotNone(session['completed_at'])

    def test_get_items_for_phase1(self):
        """Test getting items for Phase 1"""
        session_id = self.qa_session.create(self.list_id, "Test Session")
        items = self.qa_session.get_items_for_phase(session_id, 1)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['source'], 'original')

    def test_can_start_phase2(self):
        """Test can_start_phase2 validation"""
        session_id = self.qa_session.create(self.list_id, "Test Session")

        # Initially should return False
        can_start, reason = self.qa_session.can_start_phase2(session_id)
        self.assertFalse(can_start)
        self.assertIn("Phase 1", reason)


class TestQAValidationModel(unittest.TestCase):
    """Test QAValidation service class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_list = QAList(self.db)
        self.qa_item = QAItem(self.db)
        self.qa_session = QASession(self.db)
        self.qa_validation = QAValidation(self.db)

        self.list_id = self.qa_list.create("Test List")
        self.item_id = self.qa_item.create(self.list_id, "Test Item")
        self.session_id = self.qa_session.create(self.list_id, "Test Session")

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_validation(self):
        """Test creating a validation"""
        validation_id = self.qa_validation.create(
            session_id=self.session_id,
            phase=1,
            list_id=self.list_id,
            item_id=self.item_id,
            status='pass',
            actual_result='It worked',
            notes='Good',
            validator_name='John'
        )
        self.assertIsNotNone(validation_id)

    def test_validation_status_options(self):
        """Test all valid status options"""
        statuses = ['pass', 'fail', 'skip', 'blocked']
        for status in statuses:
            validation_id = self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=self.item_id,
                status=status
            )
            self.assertIsNotNone(validation_id)

    def test_get_by_session(self):
        """Test retrieving validations by session"""
        self.qa_validation.create(
            session_id=self.session_id, phase=1, list_id=self.list_id,
            item_id=self.item_id, status='pass'
        )

        validations = self.qa_validation.get_by_session(self.session_id)
        self.assertEqual(len(validations), 1)

    def test_get_by_session_filtered_by_phase(self):
        """Test retrieving validations filtered by phase"""
        # Create Phase 1 validation
        self.qa_validation.create(
            session_id=self.session_id, phase=1, list_id=self.list_id,
            item_id=self.item_id, status='pass'
        )

        phase1_vals = self.qa_validation.get_by_session(self.session_id, phase=1)
        phase2_vals = self.qa_validation.get_by_session(self.session_id, phase=2)

        self.assertEqual(len(phase1_vals), 1)
        self.assertEqual(len(phase2_vals), 0)

    def test_get_summary(self):
        """Test getting validation summary"""
        self.qa_validation.create(
            session_id=self.session_id, phase=1, list_id=self.list_id,
            item_id=self.item_id, status='pass'
        )

        summary = self.qa_validation.get_summary(session_id=self.session_id)
        self.assertEqual(summary['total_items'], 1)
        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)

    def test_get_summary_by_phase(self):
        """Test getting summary filtered by phase"""
        self.qa_validation.create(
            session_id=self.session_id, phase=1, list_id=self.list_id,
            item_id=self.item_id, status='pass'
        )

        summary_p1 = self.qa_validation.get_summary(session_id=self.session_id, phase=1)
        summary_p2 = self.qa_validation.get_summary(session_id=self.session_id, phase=2)

        self.assertEqual(summary_p1['total_items'], 1)
        self.assertEqual(summary_p2['total_items'], 0)

    def test_get_timeline(self):
        """Test getting chronological timeline"""
        self.qa_validation.create(
            session_id=self.session_id, phase=1, list_id=self.list_id,
            item_id=self.item_id, status='pass'
        )

        timeline = self.qa_validation.get_timeline(self.session_id)
        self.assertEqual(len(timeline), 1)


class TestQATemplateModel(unittest.TestCase):
    """Test QATemplate service class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_template = QATemplate(self.db)

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_template(self):
        """Test creating a template"""
        template_id = self.qa_template.create(
            "Security Checklist",
            "Standard security checks",
            "Security"
        )
        self.assertIsNotNone(template_id)

    def test_get_template_by_id(self):
        """Test retrieving template by ID"""
        template_id = self.qa_template.create("Test Template")
        template = self.qa_template.get_by_id(template_id)

        self.assertEqual(template['name'], "Test Template")
        self.assertTrue(template['is_active'])

    def test_get_all_templates(self):
        """Test retrieving all templates"""
        self.qa_template.create("Template 1")
        self.qa_template.create("Template 2")

        templates = self.qa_template.get_all()
        self.assertEqual(len(templates), 2)

    def test_add_item_to_template(self):
        """Test adding item to template"""
        template_id = self.qa_template.create("Test Template")
        item_id = self.qa_template.add_item(
            template_id,
            "Check for SQL injection",
            category="Security"
        )
        self.assertIsNotNone(item_id)

    def test_get_template_items(self):
        """Test retrieving template items"""
        template_id = self.qa_template.create("Test Template")
        self.qa_template.add_item(template_id, "Item 1")
        self.qa_template.add_item(template_id, "Item 2")

        items = self.qa_template.get_items(template_id)
        self.assertEqual(len(items), 2)


class TestQASessionPhase2ItemModel(unittest.TestCase):
    """Test QASessionPhase2Item service class"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_list = QAList(self.db)
        self.qa_session = QASession(self.db)
        self.qa_phase2_item = QASessionPhase2Item(self.db)
        self.qa_template = QATemplate(self.db)

        self.list_id = self.qa_list.create("Test List")
        self.session_id = self.qa_session.create(self.list_id, "Test Session")

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_add_manual_item(self):
        """Test adding a manual Phase 2 item"""
        item_id = self.qa_phase2_item.add_manual_item(
            self.session_id,
            "Custom test item",
            category="Custom"
        )
        self.assertIsNotNone(item_id)

    def test_manual_item_has_correct_source(self):
        """Test manual items are marked correctly"""
        self.qa_phase2_item.add_manual_item(self.session_id, "Test")
        items = self.qa_phase2_item.get_by_session(self.session_id)

        self.assertEqual(items[0]['source'], 'manual')

    def test_import_from_template(self):
        """Test importing items from template"""
        # Create template with items
        template_id = self.qa_template.create("Security Template")
        self.qa_template.add_item(template_id, "Check 1")
        self.qa_template.add_item(template_id, "Check 2")

        # Import to session
        count = self.qa_phase2_item.import_from_template(self.session_id, template_id)

        self.assertEqual(count, 2)
        items = self.qa_phase2_item.get_by_session(self.session_id)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['source'], 'template')

    def test_get_phase2_items_by_session(self):
        """Test retrieving Phase 2 items for a session"""
        self.qa_phase2_item.add_manual_item(self.session_id, "Item 1")
        self.qa_phase2_item.add_manual_item(self.session_id, "Item 2")

        items = self.qa_phase2_item.get_by_session(self.session_id)
        self.assertEqual(len(items), 2)


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for complete two-phase workflow"""

    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.db = Database()
        self.qa_list = QAList(self.db)
        self.qa_item = QAItem(self.db)
        self.qa_session = QASession(self.db)
        self.qa_validation = QAValidation(self.db)
        self.qa_phase2_item = QASessionPhase2Item(self.db)
        self.qa_template = QATemplate(self.db)

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_complete_two_phase_workflow(self):
        """Test complete workflow from list creation to Phase 2 completion"""
        # Create and publish list
        list_id = self.qa_list.create("Feature QA")
        item1 = self.qa_item.create(list_id, "Test login")
        item2 = self.qa_item.create(list_id, "Test logout")
        self.qa_list.publish(list_id)

        # Create session
        session_id = self.qa_session.create(list_id, "Sprint 1")

        # Phase 1: Developer validation
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=list_id,
            item_id=item1, status='pass', validator_name='Dev'
        )
        self.qa_validation.create(
            session_id=session_id, phase=1, list_id=list_id,
            item_id=item2, status='pass', validator_name='Dev'
        )

        # Complete Phase 1
        self.qa_session.complete_phase1(session_id, 'Developer')

        # Start Phase 2
        self.qa_session.start_phase2(session_id)

        # Phase 2: Add custom item
        phase2_item = self.qa_phase2_item.add_manual_item(
            session_id, "Test password reset"
        )

        # Phase 2: QA validation
        self.qa_validation.create(
            session_id=session_id, phase=2, list_id=list_id,
            item_id=item1, status='pass', validator_name='QA'
        )

        # Complete Phase 2
        self.qa_session.complete_phase2(session_id, 'QA Engineer')

        # Verify session state
        session = self.qa_session.get_by_id(session_id)
        self.assertIsNotNone(session['completed_at'])
        self.assertEqual(session['phase1_completed_by'], 'Developer')
        self.assertEqual(session['phase2_completed_by'], 'QA Engineer')

        # Verify validations
        summary = self.qa_validation.get_summary(session_id=session_id)
        self.assertEqual(summary['total_items'], 3)  # 2 phase1 + 1 phase2


if __name__ == '__main__':
    unittest.main()
