# Two-Phase QA Feature - Testing Guide

## Prerequisites

You need Python 3.12+ with the following packages installed:
- Flask
- SQLAlchemy
- psycopg2-binary (for PostgreSQL, optional)

## Quick Start

### 1. Install Dependencies

```bash
# Option 1: Using pip with virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 2: Using pip with --user flag
pip install --user flask sqlalchemy

# Option 3: System-wide (not recommended)
sudo apt install python3-flask python3-sqlalchemy  # Debian/Ubuntu
```

### 2. Run Automated Tests

```bash
python3 test_setup.py
```

This will:
- ✅ Validate all imports
- ✅ Initialize the database schema
- ✅ Create sample data (QA list, items, template, session)
- ✅ Test the complete two-phase workflow
- ✅ Verify Phase 1 → Phase 2 transition
- ✅ Test Phase 2 custom items
- ✅ Verify validation tracking and summaries

### 3. Start the Application

```bash
python3 app.py
```

Visit http://localhost:5000

## Manual Testing Workflow

### Test Case 1: Create and Publish a QA List

1. Navigate to http://localhost:5000
2. Click "Create New List"
3. Fill in:
   - Name: "User Login Feature QA"
   - Description: "Testing the new login functionality"
4. Click "Create"
5. Add QA items:
   - Item 1: "Test login with valid credentials" (Category: Functionality)
   - Item 2: "Test login with invalid credentials" (Category: Security)
   - Item 3: "Test password reset flow" (Category: Functionality)
6. Click "Publish" button

### Test Case 2: Phase 1 - Developer QA

1. Navigate to "Published Lists"
2. Find your list and click "Create New Session"
3. Enter session name: "Sprint 23 Testing"
4. Click "Start Phase 1"
5. For each item:
   - Select status (Pass/Fail/Skip/Blocked)
   - Enter actual result
   - Enter notes
   - Enter your name (e.g., "Developer John")
   - Click "Record Validation"
6. After validating all items, scroll to bottom
7. Enter your name in "Complete Phase 1" form
8. Click "Complete Phase 1"
9. Verify: You see "Phase 1 completed successfully" message

### Test Case 3: Phase 2 - QA Engineer Testing

1. From "Published Lists", find your session (should show "Phase 2" badge)
2. Click "Start Phase 2" button
3. Click "Continue Phase 2"
4. Validate the original items again:
   - Select different statuses to test independently
   - Enter "QA Engineer Sarah" as validator name
5. Test adding a custom item:
   - Click "+ Add Custom Item"
   - Fill in description: "Test logout functionality"
   - Click "Add Item"
   - Verify: New item appears at bottom
6. Test importing from template:
   - First, create a template (navigate to /templates/manage)
   - Back in Phase 2, select template from dropdown
   - Verify: Template items are imported
7. Complete Phase 2:
   - Enter your name
   - Click "Complete Phase 2"

### Test Case 4: View Results

1. Navigate to session results
2. Verify three tabs appear: "Phase 1 Results", "Phase 2 Results", "Timeline"
3. **Phase 1 Tab:**
   - Verify summary cards show correct counts
   - Verify validation table shows only Phase 1 validations
   - Verify validator name shows "Developer John"
4. **Phase 2 Tab:**
   - Verify summary cards show Phase 2 counts
   - Verify table shows Phase 2 validations
   - Verify Phase 2 custom items are marked with badge
   - Verify validator name shows "QA Engineer Sarah"
5. **Timeline Tab:**
   - Verify all validations appear chronologically
   - Verify each row has a phase badge (Phase 1 or Phase 2)
   - Verify timeline includes both original and Phase 2 items

### Test Case 5: Template Management

1. Navigate to /templates/manage
2. Create a template:
   - Name: "Security Checklist"
   - Description: "Standard security validations"
   - Category: "Security"
3. Add items to template:
   - "Test for SQL injection"
   - "Test for XSS vulnerabilities"
   - "Test authentication bypass"
4. Use template in Phase 2 session (see Test Case 3)

## Expected Behavior

### Phase Workflow
- ✅ Phase 1 cannot be completed until all original items are validated
- ✅ Phase 2 cannot be started until Phase 1 is complete
- ✅ Phase 2 validations are separate from Phase 1 (same item can have both)
- ✅ Phase 2 can add custom items and import from templates
- ✅ Completed sessions show "Completed" badge

### Data Integrity
- ✅ Each validation tracks: session_id, phase, item_id, status, validator, timestamp
- ✅ Phase 2 custom items have their own IDs and source tracking
- ✅ Template imports preserve category, description, expected result
- ✅ Deleting a session cascades to all validations and Phase 2 items

### UI Features
- ✅ Session cards show current phase and completion status
- ✅ Phase badges use different colors (Phase 1: warning/orange, Phase 2: info/blue)
- ✅ Results tabs switch properly
- ✅ AJAX form submission works without page reload
- ✅ Auto-scroll to next item after validation

## Troubleshooting

### Database Errors
```bash
# Reset database
rm qa_tracker.db
python3 test_setup.py
```

### Import Errors
```bash
# Make sure Flask and SQLAlchemy are installed
pip list | grep -i flask
pip list | grep -i sqlalchemy
```

### Port Already in Use
```bash
# Change port in app.py (line 409)
app.run(debug=True, port=5001)  # Use different port
```

## Database Schema Verification

To verify the database schema was created correctly:

```bash
sqlite3 qa_tracker.db ".schema"
```

Expected tables:
- qa_lists
- qa_items
- qa_validations
- qa_sessions
- qa_templates
- qa_template_items
- qa_session_phase2_items

## Success Criteria

The implementation is working correctly if:
1. ✅ All automated tests pass
2. ✅ Phase 1 → Phase 2 workflow enforces sequential completion
3. ✅ Phase 2 can add custom items via modal
4. ✅ Phase 2 can import items from templates
5. ✅ Results page shows three tabs with correct data
6. ✅ Phase badges distinguish Phase 1 from Phase 2
7. ✅ Validations are tracked separately per phase
8. ✅ No database errors or constraint violations

## Next Steps

If all tests pass:
1. Update CSS in `/static/css/style.css` for better styling
2. Add more comprehensive error handling
3. Add user authentication
4. Add export functionality (PDF, CSV)
5. Add email notifications for phase completions

## Support

If you encounter issues:
1. Check the console for error messages
2. Verify database schema matches expected structure
3. Ensure all dependencies are installed
4. Review the implementation plan at `.claude/plans/smooth-exploring-wilkes.md`
