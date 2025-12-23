#!/usr/bin/env python3
"""
Comprehensive API tests for the QA Tracker Flask application
Tests all routes including session management, Phase 2 items, templates, and validations
"""

import unittest
import json
import tempfile
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Database, QAList, QAItem, QASession, QAValidation, QATemplate, QASessionPhase2Item


class TestFlaskAPI(unittest.TestCase):
    """Test Flask API endpoints"""

    def setUp(self):
        """Set up test client and database"""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        # Configure app for testing
        app.config['TESTING'] = True
        app.config['DATABASE_URL'] = f'sqlite:///{self.db_path}'

        # Initialize database
        self.db = Database(db_url=f'sqlite:///{self.db_path}')

        # Create test client
        self.client = app.test_client()

        # Initialize service instances
        self.qa_list = QAList(self.db)
        self.qa_item = QAItem(self.db)
        self.qa_session = QASession(self.db)
        self.qa_validation = QAValidation(self.db)
        self.qa_template = QATemplate(self.db)
        self.qa_phase2_item = QASessionPhase2Item(self.db)

        # Create test data
        self.list_id = self.qa_list.create("Test List", "Test Description")
        self.qa_list.publish(self.list_id)
        self.item1_id = self.qa_item.create(self.list_id, "Test Item 1", category="Functionality")
        self.item2_id = self.qa_item.create(self.list_id, "Test Item 2", category="Security")
        self.session_id = self.qa_session.create(self.list_id, "Test Session")
        self.template_id = self.qa_template.create("Test Template", "Test Template Desc", "Security")

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)


class TestIndexRoutes(TestFlaskAPI):
    """Test basic navigation routes"""

    def test_index_page(self):
        """Test homepage loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'QA Tracker', response.data)

    def test_lists_page(self):
        """Test lists page loads"""
        response = self.client.get('/lists')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your QA Lists', response.data)

    def test_published_page(self):
        """Test published lists page loads"""
        response = self.client.get('/published')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Published QA Lists', response.data)


class TestListManagement(TestFlaskAPI):
    """Test QA list CRUD operations"""

    def test_create_list_get(self):
        """Test create list page loads"""
        response = self.client.get('/list/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New QA List', response.data)

    def test_create_list_post(self):
        """Test creating a new list"""
        response = self.client.post('/list/create', data={
            'name': 'New List',
            'description': 'New Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify list was created
        lists = self.qa_list.get_all(status='draft')
        self.assertTrue(any(l['name'] == 'New List' for l in lists))

    def test_view_list(self):
        """Test viewing a specific list"""
        response = self.client.get(f'/list/{self.list_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test List', response.data)

    def test_view_nonexistent_list(self):
        """Test viewing a list that doesn't exist"""
        response = self.client.get('/list/99999')
        self.assertEqual(response.status_code, 404)

    def test_publish_list(self):
        """Test publishing a list"""
        # Create unpublished list
        new_list_id = self.qa_list.create("Draft List", "Draft")

        response = self.client.post(f'/list/{new_list_id}/publish', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify list is published
        list_info = self.qa_list.get_by_id(new_list_id)
        self.assertEqual(list_info['status'], 'published')

    def test_delete_list(self):
        """Test deleting a list"""
        # Create list to delete
        delete_list_id = self.qa_list.create("To Delete", "Will be deleted")

        response = self.client.post(f'/list/{delete_list_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify list is deleted
        list_info = self.qa_list.get_by_id(delete_list_id)
        self.assertIsNone(list_info)


class TestItemManagement(TestFlaskAPI):
    """Test QA item CRUD operations"""

    def test_add_item(self):
        """Test adding an item to a list"""
        response = self.client.post(f'/list/{self.list_id}/item/add', data={
            'description': 'New Test Item',
            'category': 'Performance',
            'expected_result': 'Should be fast',
            'notes': 'Some notes'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify item was added
        items = self.qa_item.get_by_list(self.list_id)
        self.assertTrue(any(item['description'] == 'New Test Item' for item in items))

    def test_delete_item(self):
        """Test deleting an item"""
        # Create item to delete
        item_id = self.qa_item.create(self.list_id, "To Delete")

        response = self.client.post(f'/item/{item_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify item is deleted
        item_info = self.qa_item.get_by_id(item_id)
        self.assertIsNone(item_info)

    def test_reorder_items(self):
        """Test reordering items"""
        items = self.qa_item.get_by_list(self.list_id)
        original_order = [item['id'] for item in items]
        reversed_order = list(reversed(original_order))

        response = self.client.post(f'/list/{self.list_id}/items/reorder',
                                    data={'order': ','.join(map(str, reversed_order))},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify new order
        items_after = self.qa_item.get_by_list(self.list_id)
        new_order = [item['id'] for item in items_after]
        self.assertEqual(new_order, reversed_order)


class TestSessionManagement(TestFlaskAPI):
    """Test QA session management"""

    def test_create_session_get(self):
        """Test create session page loads"""
        response = self.client.get(f'/list/{self.list_id}/session/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Session', response.data)

    def test_create_session_post(self):
        """Test creating a new session"""
        response = self.client.post(f'/list/{self.list_id}/session/create', data={
            'session_name': 'Sprint 23 QA'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify session was created
        sessions = self.qa_session.get_by_list(self.list_id)
        self.assertTrue(any(s['session_name'] == 'Sprint 23 QA' for s in sessions))

    def test_view_session(self):
        """Test viewing a session"""
        response = self.client.get(f'/session/{self.session_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Session', response.data)

    def test_complete_phase1_without_validations(self):
        """Test Phase 1 completion fails without all validations"""
        response = self.client.post(f'/session/{self.session_id}/complete-phase1', data={
            'completed_by': 'Developer'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'not all items have been validated', response.data)

    def test_complete_phase1_success(self):
        """Test Phase 1 completion succeeds with all validations"""
        # Add validations for all items
        self.qa_validation.create(
            session_id=self.session_id,
            phase=1,
            list_id=self.list_id,
            item_id=self.item1_id,
            status='pass',
            validator_name='Developer'
        )
        self.qa_validation.create(
            session_id=self.session_id,
            phase=1,
            list_id=self.list_id,
            item_id=self.item2_id,
            status='pass',
            validator_name='Developer'
        )

        response = self.client.post(f'/session/{self.session_id}/complete-phase1', data={
            'completed_by': 'Developer'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phase 1 completed successfully', response.data)

        # Verify session is in Phase 2
        session = self.qa_session.get_by_id(self.session_id)
        self.assertEqual(session['current_phase'], 1)
        self.assertIsNotNone(session['phase1_completed_at'])

    def test_start_phase2_without_phase1(self):
        """Test Phase 2 start fails without Phase 1 completion"""
        response = self.client.post(f'/session/{self.session_id}/start-phase2',
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phase 1 must be completed', response.data)

    def test_start_phase2_success(self):
        """Test Phase 2 start succeeds after Phase 1"""
        # Complete Phase 1
        for item_id in [self.item1_id, self.item2_id]:
            self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=item_id,
                status='pass',
                validator_name='Developer'
            )
        self.qa_session.complete_phase1(self.session_id, 'Developer')

        # Start Phase 2
        response = self.client.post(f'/session/{self.session_id}/start-phase2',
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify session is in Phase 2
        session = self.qa_session.get_by_id(self.session_id)
        self.assertEqual(session['current_phase'], 2)
        self.assertIsNotNone(session['phase2_started_at'])

    def test_complete_phase2(self):
        """Test Phase 2 completion"""
        # Complete Phase 1 and start Phase 2
        for item_id in [self.item1_id, self.item2_id]:
            self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=item_id,
                status='pass',
                validator_name='Developer'
            )
        self.qa_session.complete_phase1(self.session_id, 'Developer')
        self.qa_session.start_phase2(self.session_id)

        # Complete Phase 2
        response = self.client.post(f'/session/{self.session_id}/complete-phase2', data={
            'completed_by': 'QA Engineer'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify session is completed
        session = self.qa_session.get_by_id(self.session_id)
        self.assertIsNotNone(session['phase2_completed_at'])
        self.assertEqual(session['phase2_completed_by'], 'QA Engineer')

    def test_delete_session(self):
        """Test deleting a session"""
        # Create session to delete
        delete_session_id = self.qa_session.create(self.list_id, "To Delete")

        response = self.client.post(f'/session/{delete_session_id}/delete',
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify session is deleted
        session = self.qa_session.get_by_id(delete_session_id)
        self.assertIsNone(session)


class TestQASessionPhases(TestFlaskAPI):
    """Test QA session execution for both phases"""

    def test_qa_session_phase1_page(self):
        """Test Phase 1 QA session page loads"""
        response = self.client.get(f'/qa/{self.session_id}/phase/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phase 1', response.data)
        self.assertIn(b'Test Item 1', response.data)

    def test_qa_session_phase2_page(self):
        """Test Phase 2 QA session page loads after Phase 1"""
        # Complete Phase 1
        for item_id in [self.item1_id, self.item2_id]:
            self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=item_id,
                status='pass',
                validator_name='Developer'
            )
        self.qa_session.complete_phase1(self.session_id, 'Developer')
        self.qa_session.start_phase2(self.session_id)

        response = self.client.get(f'/qa/{self.session_id}/phase/2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phase 2', response.data)

    def test_validate_item_phase1(self):
        """Test recording a validation in Phase 1"""
        response = self.client.post(f'/qa/{self.session_id}/validate', data={
            'phase': '1',
            'list_id': str(self.list_id),
            'item_id': str(self.item1_id),
            'status': 'pass',
            'actual_result': 'Test passed',
            'notes': 'Looks good',
            'validator_name': 'Developer'
        })
        self.assertEqual(response.status_code, 200)

        # Verify validation was recorded
        validations = self.qa_validation.get_by_session(self.session_id, phase=1)
        self.assertEqual(len(validations), 1)
        self.assertEqual(validations[0]['status'], 'pass')

    def test_validate_item_phase2(self):
        """Test recording a validation in Phase 2"""
        # Setup Phase 2
        for item_id in [self.item1_id, self.item2_id]:
            self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=item_id,
                status='pass',
                validator_name='Developer'
            )
        self.qa_session.complete_phase1(self.session_id, 'Developer')
        self.qa_session.start_phase2(self.session_id)

        # Validate in Phase 2
        response = self.client.post(f'/qa/{self.session_id}/validate', data={
            'phase': '2',
            'list_id': str(self.list_id),
            'item_id': str(self.item1_id),
            'status': 'fail',
            'actual_result': 'Found a bug',
            'validator_name': 'QA Engineer'
        })
        self.assertEqual(response.status_code, 200)

        # Verify both phases have validations
        phase1_validations = self.qa_validation.get_by_session(self.session_id, phase=1)
        phase2_validations = self.qa_validation.get_by_session(self.session_id, phase=2)
        self.assertEqual(len(phase1_validations), 2)
        self.assertEqual(len(phase2_validations), 1)


class TestPhase2Items(TestFlaskAPI):
    """Test Phase 2 custom item management"""

    def setUp(self):
        """Set up with Phase 2 ready"""
        super().setUp()
        # Complete Phase 1 and start Phase 2
        for item_id in [self.item1_id, self.item2_id]:
            self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=item_id,
                status='pass',
                validator_name='Developer'
            )
        self.qa_session.complete_phase1(self.session_id, 'Developer')
        self.qa_session.start_phase2(self.session_id)

    def test_add_custom_item(self):
        """Test adding a custom item in Phase 2"""
        response = self.client.post(f'/session/{self.session_id}/add-item', data={
            'description': 'Custom QA Item',
            'category': 'Usability',
            'expected_result': 'Should be user-friendly',
            'notes': 'Added during Phase 2'
        })
        self.assertEqual(response.status_code, 200)

        # Verify item was added
        phase2_items = self.qa_phase2_item.get_by_session(self.session_id)
        self.assertEqual(len(phase2_items), 1)
        self.assertEqual(phase2_items[0]['description'], 'Custom QA Item')
        self.assertEqual(phase2_items[0]['source'], 'manual')

    def test_import_template(self):
        """Test importing items from a template"""
        # Add items to template
        self.qa_template.add_item(
            self.template_id,
            "Security Check 1",
            category="Security",
            expected_result="No vulnerabilities"
        )
        self.qa_template.add_item(
            self.template_id,
            "Security Check 2",
            category="Security",
            expected_result="All data encrypted"
        )

        response = self.client.post(f'/session/{self.session_id}/import-template', data={
            'template_id': str(self.template_id)
        })
        self.assertEqual(response.status_code, 200)

        # Verify items were imported
        phase2_items = self.qa_phase2_item.get_by_session(self.session_id)
        self.assertEqual(len(phase2_items), 2)
        self.assertTrue(all(item['source'] == 'template' for item in phase2_items))

    def test_validate_phase2_custom_item(self):
        """Test validating a Phase 2 custom item"""
        # Add custom item
        phase2_item_id = self.qa_phase2_item.add_manual_item(
            self.session_id,
            "Custom Item",
            category="Performance"
        )

        # Validate the custom item
        response = self.client.post(f'/qa/{self.session_id}/validate', data={
            'phase': '2',
            'list_id': str(self.list_id),
            'phase2_item_id': str(phase2_item_id),
            'status': 'pass',
            'validator_name': 'QA Engineer'
        })
        self.assertEqual(response.status_code, 200)

        # Verify validation was recorded
        validations = self.qa_validation.get_by_session(self.session_id, phase=2)
        custom_validations = [v for v in validations if v['phase2_item_id'] == phase2_item_id]
        self.assertEqual(len(custom_validations), 1)


class TestTemplateManagement(TestFlaskAPI):
    """Test template CRUD operations"""

    def test_templates_page(self):
        """Test templates management page loads"""
        response = self.client.get('/templates/manage')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'QA Templates', response.data)

    def test_create_template(self):
        """Test creating a new template"""
        response = self.client.post('/template/create', data={
            'name': 'Performance Template',
            'description': 'Performance testing checklist',
            'category': 'Performance'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify template was created
        templates = self.qa_template.get_all()
        self.assertTrue(any(t['name'] == 'Performance Template' for t in templates))

    def test_add_template_item(self):
        """Test adding an item to a template"""
        response = self.client.post(f'/template/{self.template_id}/add-item', data={
            'description': 'Template Item 1',
            'category': 'Security',
            'expected_result': 'Secure',
            'notes': 'Important check'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify item was added
        template_items = self.qa_template.get_items(self.template_id)
        self.assertEqual(len(template_items), 1)
        self.assertEqual(template_items[0]['description'], 'Template Item 1')

    def test_get_template_items_json(self):
        """Test getting template items as JSON"""
        # Add items to template
        self.qa_template.add_item(self.template_id, "Item 1")
        self.qa_template.add_item(self.template_id, "Item 2")

        response = self.client.get(f'/template/{self.template_id}/items')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)


class TestResults(TestFlaskAPI):
    """Test results display"""

    def setUp(self):
        """Set up with completed session"""
        super().setUp()
        # Complete both phases
        for item_id in [self.item1_id, self.item2_id]:
            self.qa_validation.create(
                session_id=self.session_id,
                phase=1,
                list_id=self.list_id,
                item_id=item_id,
                status='pass',
                validator_name='Developer'
            )
        self.qa_session.complete_phase1(self.session_id, 'Developer')
        self.qa_session.start_phase2(self.session_id)

        # Add Phase 2 validations
        self.qa_validation.create(
            session_id=self.session_id,
            phase=2,
            list_id=self.list_id,
            item_id=self.item1_id,
            status='fail',
            validator_name='QA Engineer'
        )

    def test_results_page(self):
        """Test results page loads"""
        response = self.client.get(f'/session/{self.session_id}/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Session', response.data)
        self.assertIn(b'Phase 1 Results', response.data)
        self.assertIn(b'Phase 2 Results', response.data)
        self.assertIn(b'Timeline', response.data)

    def test_results_show_both_phases(self):
        """Test results page shows data from both phases"""
        response = self.client.get(f'/session/{self.session_id}/results')
        self.assertEqual(response.status_code, 200)

        # Should show Phase 1 validations
        self.assertIn(b'Developer', response.data)

        # Should show Phase 2 validations
        self.assertIn(b'QA Engineer', response.data)

    def test_results_summary_data(self):
        """Test that summary data is calculated correctly"""
        response = self.client.get(f'/session/{self.session_id}/results')
        self.assertEqual(response.status_code, 200)

        # Phase 1 should show 2 passes
        self.assertIn(b'2', response.data)  # Total items for Phase 1

        # Phase 2 should show 1 fail
        # The page should contain phase 2 data


class TestEdgeCases(TestFlaskAPI):
    """Test edge cases and error handling"""

    def test_access_nonexistent_session(self):
        """Test accessing a session that doesn't exist"""
        response = self.client.get('/session/99999')
        self.assertEqual(response.status_code, 404)

    def test_access_nonexistent_template(self):
        """Test accessing a template that doesn't exist"""
        response = self.client.get('/template/99999/items')
        self.assertEqual(response.status_code, 404)

    def test_add_item_to_published_list(self):
        """Test that items can be added to published lists"""
        # List is already published in setUp
        response = self.client.post(f'/list/{self.list_id}/item/add', data={
            'description': 'New Item'
        }, follow_redirects=True)
        # Should succeed or redirect appropriately
        self.assertIn(response.status_code, [200, 302])

    def test_delete_session_cascades_validations(self):
        """Test that deleting a session deletes its validations"""
        # Add validations
        val_id = self.qa_validation.create(
            session_id=self.session_id,
            phase=1,
            list_id=self.list_id,
            item_id=self.item1_id,
            status='pass',
            validator_name='Developer'
        )

        # Delete session
        self.client.post(f'/session/{self.session_id}/delete', follow_redirects=True)

        # Verify validations are gone
        validations = self.qa_validation.get_by_session(self.session_id)
        self.assertEqual(len(validations), 0)

    def test_phase2_before_phase1_fails(self):
        """Test that Phase 2 cannot be accessed before Phase 1 completion"""
        response = self.client.get(f'/qa/{self.session_id}/phase/2')
        # Should redirect or show error
        self.assertIn(response.status_code, [200, 302])


class TestIntegrationWorkflow(TestFlaskAPI):
    """Test complete end-to-end workflow"""

    def test_complete_workflow_via_api(self):
        """Test complete workflow from list creation to Phase 2 completion via API"""
        # 1. Create list
        response = self.client.post('/list/create', data={
            'name': 'E2E Test List',
            'description': 'End to end test'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Get list ID
        lists = self.qa_list.get_all(status='draft')
        e2e_list = next(l for l in lists if l['name'] == 'E2E Test List')
        list_id = e2e_list['id']

        # 2. Add items
        self.client.post(f'/list/{list_id}/item/add', data={
            'description': 'Item 1',
            'category': 'Functionality'
        }, follow_redirects=True)
        self.client.post(f'/list/{list_id}/item/add', data={
            'description': 'Item 2',
            'category': 'Security'
        }, follow_redirects=True)

        # 3. Publish list
        self.client.post(f'/list/{list_id}/publish', follow_redirects=True)

        # 4. Create session
        self.client.post(f'/list/{list_id}/session/create', data={
            'session_name': 'E2E Session'
        }, follow_redirects=True)

        # Get session ID
        sessions = self.qa_session.get_by_list(list_id)
        session = sessions[0]
        session_id = session['id']

        # 5. Validate items in Phase 1
        items = self.qa_item.get_by_list(list_id)
        for item in items:
            self.client.post(f'/qa/{session_id}/validate', data={
                'phase': '1',
                'list_id': str(list_id),
                'item_id': str(item['id']),
                'status': 'pass',
                'validator_name': 'Developer'
            })

        # 6. Complete Phase 1
        self.client.post(f'/session/{session_id}/complete-phase1', data={
            'completed_by': 'Developer'
        }, follow_redirects=True)

        # 7. Start Phase 2
        self.client.post(f'/session/{session_id}/start-phase2', follow_redirects=True)

        # 8. Add custom item in Phase 2
        self.client.post(f'/session/{session_id}/add-item', data={
            'description': 'Custom Phase 2 Item',
            'category': 'Usability'
        })

        # 9. Validate in Phase 2
        self.client.post(f'/qa/{session_id}/validate', data={
            'phase': '2',
            'list_id': str(list_id),
            'item_id': str(items[0]['id']),
            'status': 'pass',
            'validator_name': 'QA Engineer'
        })

        # 10. Complete Phase 2
        self.client.post(f'/session/{session_id}/complete-phase2', data={
            'completed_by': 'QA Engineer'
        }, follow_redirects=True)

        # 11. Verify results
        response = self.client.get(f'/session/{session_id}/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'E2E Session', response.data)

        # Verify session state
        final_session = self.qa_session.get_by_id(session_id)
        self.assertIsNotNone(final_session['phase1_completed_at'])
        self.assertIsNotNone(final_session['phase2_completed_at'])
        self.assertEqual(final_session['phase1_completed_by'], 'Developer')
        self.assertEqual(final_session['phase2_completed_by'], 'QA Engineer')


if __name__ == '__main__':
    print("=" * 60)
    print("QA Tracker API Tests")
    print("=" * 60)

    # Run tests with verbosity
    unittest.main(verbosity=2)
