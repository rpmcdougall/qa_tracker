# QA Tracker - MVC Application

A simple Python Flask MVC application for managing QA checklists and tracking validation work. Supports multiple database backends including SQLite, PostgreSQL, MySQL, Snowflake, and Databricks.

## Features

- **Create QA Lists**: Define comprehensive QA checklists for your development work
- **Organize Items**: Add detailed test items with categories, expected results, and notes
- **Publish Lists**: Publish finalized lists to make them available for QA sessions
- **Two-Phase QA Sessions**: Developer validation (Phase 1) followed by QA Engineer review (Phase 2)
- **Session Management**: Create named sessions to track validation work over time
- **Phase 2 Customization**: Add custom test items and import from templates during QA review
- **Template System**: Create reusable QA checklists for common testing scenarios
- **Track Results**: View validation history with separate Phase 1 and Phase 2 results, plus chronological timeline
- **Show Your Work**: Document exactly what you tested and the results
- **Multiple Database Support**: Use SQLite (default), PostgreSQL, MySQL, Snowflake, or Databricks as your backend

## Architecture

This application follows the MVC (Model-View-Controller) pattern with SQLAlchemy ORM:

- **Models** (`models.py`): Database layer with SQLAlchemy
  - `Database`: Connection management and schema initialization
  - `QAList`: CRUD operations for QA lists
  - `QAItem`: Managing individual test items
  - `QASession`: Two-phase session management and workflow
  - `QAValidation`: Recording and retrieving validation results by phase
  - `QATemplate`: Reusable QA checklist templates
  - `QASessionPhase2Item`: Custom items added during Phase 2
  - Supports SQLite, PostgreSQL, MySQL, Snowflake, and Databricks

- **Controllers** (`app.py`): Flask routes handling business logic
  - List management (create, view, publish, delete)
  - Item management (add, delete, reorder)
  - Session management (create, Phase 1/2 workflow, complete)
  - Phase 2 item management (add custom items, import templates)
  - Template management (create, add items)
  - QA validation recording (Phase 1 and Phase 2)
  - Results viewing (separate Phase 1, Phase 2, and Timeline tabs)

- **Views** (`templates/`): HTML templates with Jinja2
  - List views (index, create, view)
  - QA session interface
  - Results dashboard

## Installation

### Quick Start (SQLite - Default)

1. **Clone or download this directory**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open in browser**:
   Navigate to `http://localhost:5000`

### Using Other Databases

To use PostgreSQL, MySQL, Snowflake, or Databricks instead of SQLite:

1. **Set the DATABASE_URL environment variable**:
   ```bash
   # PostgreSQL
   export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/qa_tracker"
   
   # MySQL
   export DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/qa_tracker"
   
   # Snowflake
   export DATABASE_URL="snowflake://user:pass@account.region/db/schema?warehouse=wh&role=role"
   
   # Databricks
   export DATABASE_URL="databricks://token:your_token@workspace.cloud.databricks.com:443/catalog.schema?http_path=/sql/1.0/warehouses/id"
   ```

2. **Install the appropriate database driver** (already in requirements.txt)

3. **Test the connection**:
   ```bash
   python test_db_connection.py
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

For detailed database setup instructions, see **[DATABASE_SETUP.md](DATABASE_SETUP.md)**.

## Usage Workflow

### 1. Create a QA List

1. Click "Create New List" from the homepage
2. Enter a name (e.g., "User Login Flow QA")
3. Add a description of what this list covers
4. Click "Create List"

### 2. Add QA Items

1. From the list view, click "Add Item"
2. Fill in:
   - **Category**: e.g., "Functionality", "UI", "Performance"
   - **Description**: What to test (e.g., "Verify user can log in with valid credentials")
   - **Expected Result**: What should happen (e.g., "User redirected to dashboard")
   - **Notes**: Additional context or test data needed
3. Repeat for all test cases

### 3. Publish the List

1. Review all items in your list
2. Click "Publish" when ready
3. Published lists become available for QA sessions

### 4. Create a QA Session

1. Go to "Published Lists"
2. Click "Create New Session" on your list
3. Enter a session name (e.g., "Sprint 23 Testing")
4. Click "Start Phase 1"

### 5. Phase 1 - Developer QA

1. For each item in the list:
   - Read the description and expected result
   - Perform the test
   - Select status: Pass, Fail, Skip, or Blocked
   - Record actual result and any notes
   - Enter your name as validator
   - Click "Record Validation"
2. The app will auto-scroll to the next item
3. After validating all items, enter your name and click "Complete Phase 1"

### 6. Phase 2 - QA Engineer Review

1. Click "Start Phase 2" from the session view
2. Re-validate original items (separate from Phase 1 validations):
   - Test each item independently
   - Record your own findings
3. Add custom test items (optional):
   - Click "+ Add Custom Item"
   - Fill in description, category, expected result
   - Validate the custom item
4. Import from templates (optional):
   - Select a template from the dropdown
   - Click "Import Template Items"
   - Validate imported items
5. After completing all validations, enter your name and click "Complete Phase 2"

### 7. View Results

1. Click "View Results" from the session
2. See three tabs:
   - **Phase 1 Results**: Developer validations and summary stats
   - **Phase 2 Results**: QA Engineer validations, includes custom items
   - **Timeline**: Chronological view of all validations from both phases
3. Use this to show stakeholders what was tested in each phase

### 8. Manage Templates (Optional)

1. Navigate to "Manage Templates"
2. Create reusable QA checklists for common scenarios (e.g., "Security Checklist")
3. Add items to templates
4. Import template items during Phase 2 of any session

## Database Schema

```sql
-- QA Lists
qa_lists (
    id, name, description, created_at, updated_at, status
)

-- QA Items (test cases)
qa_items (
    id, list_id, item_order, category, description,
    expected_result, notes
)

-- QA Sessions (two-phase workflow tracking)
qa_sessions (
    id, list_id, session_name, created_at,
    current_phase, phase1_started_at, phase1_completed_at, phase1_completed_by,
    phase2_started_at, phase2_completed_at, phase2_completed_by
)

-- QA Validations (results from both phases)
qa_validations (
    id, session_id, phase, list_id, item_id, phase2_item_id,
    validated_at, status, actual_result, notes, validator_name
)

-- QA Templates (reusable checklists)
qa_templates (
    id, name, description, category, is_active, created_at, updated_at
)

-- QA Template Items
qa_template_items (
    id, template_id, item_order, category, description,
    expected_result, notes
)

-- QA Session Phase 2 Items (custom items added during Phase 2)
qa_session_phase2_items (
    id, session_id, item_order, category, description,
    expected_result, notes, source, template_id, created_at
)
```

**Note**: This schema is automatically created by SQLAlchemy ORM and works across all supported databases (SQLite, PostgreSQL, MySQL, Snowflake, Databricks). The ORM handles database-specific syntax differences.

## Use Cases

### Data Pipeline Validation
Create lists like "ETL Pipeline QA":
- Verify source data extraction
- Check transformation logic
- Validate data quality rules
- Confirm target load success

### Feature Release QA
Track validation for new features:
- Functionality tests
- UI/UX validation
- Performance checks
- Security review

### Bug Fix Verification
Document regression testing:
- Original bug reproduction
- Fix verification
- Related functionality checks
- Performance impact

## Example QA List Structure

**List Name**: "Customer Data ETL Pipeline QA"

**Items**:
1. **Category**: Data Extraction
   - **Description**: Verify source system connection and data pull
   - **Expected**: All customer records from past 24 hours extracted
   - **Notes**: Check connection logs, row counts should match source

2. **Category**: Data Transformation
   - **Description**: Validate phone number formatting
   - **Expected**: All phone numbers in (XXX) XXX-XXXX format
   - **Notes**: Sample check first 100 records

3. **Category**: Data Quality
   - **Description**: Check for duplicate customer IDs
   - **Expected**: Zero duplicates in final dataset
   - **Notes**: Run SQL: SELECT customer_id, COUNT(*) ... GROUP BY ... HAVING COUNT(*) > 1

4. **Category**: Data Load
   - **Description**: Confirm successful load to target table
   - **Expected**: Row count matches transformed dataset
   - **Notes**: Check Databricks job logs for errors

## Extending the Application

### Add New Features

**Session Tracking**:
Modify `models.py` to use the `qa_sessions` table for grouping validations by date/time sessions.

**Export Results**:
Add routes to export validation results to CSV or PDF.

**User Authentication**:
Add Flask-Login to track who creates and validates lists.

**Comments/Discussion**:
Add a comments table for team collaboration on specific items.

### Customize for Your Workflow

**Add Custom Statuses**:
Modify the CHECK constraint in `qa_validations.status` to include your own statuses.

**Add Item Types**:
Extend `qa_items` with an `item_type` field (manual, automated, exploratory).

**Priority Levels**:
Add a `priority` field to items (P0, P1, P2).

## Tips for Effective QA Lists

1. **Be Specific**: Each item should test one clear thing
2. **Include Context**: Add notes about test data or prerequisites
3. **Expected Results**: Define success criteria clearly
4. **Categories**: Group related tests for better organization
5. **Regular Updates**: Keep lists current as features change

## Troubleshooting

**Database locked errors**:
SQLite has limitations with concurrent writes. For high-concurrency needs, consider PostgreSQL.

**Port 5000 in use**:
Change the port in `app.py`: `app.run(debug=True, port=5001)`

**Flash messages not showing**:
Ensure you have a secret key set in `app.py`

## Testing

For comprehensive testing documentation and guides, see **[TESTING.md](TESTING.md)**.

The application includes:
- Automated test setup script (`test_setup.py`)
- Comprehensive model unit tests (`tests/test_models.py`)
- Full API endpoint tests (`tests/test_api.py`)
- Manual testing workflow documentation

Run tests with:
```bash
python test_setup.py
python -m unittest discover tests
```

## Future Enhancements

- Test automation integration
- Jira/GitHub issue linking
- Email notifications for phase completions
- Test metrics and trends dashboard
- Screenshot attachments for validations
- Multi-user support with authentication and roles
- Export results to PDF/CSV
- API for CI/CD integration

## License

Free to use and modify for your needs.
