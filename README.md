# QA Tracker - MVC Application

A simple Python Flask MVC application for managing QA checklists and tracking validation work. Built with SQLite for easy setup and portability.

## Features

- **Create QA Lists**: Define comprehensive QA checklists for your development work
- **Organize Items**: Add detailed test items with categories, expected results, and notes
- **Publish Lists**: Publish finalized lists to make them available for QA sessions
- **Conduct QA Sessions**: Step through each item and record validation results
- **Track Results**: View validation history and summary statistics
- **Show Your Work**: Document exactly what you tested and the results

## Architecture

This application follows the MVC (Model-View-Controller) pattern:

- **Models** (`models.py`): Database layer with SQLite
  - `Database`: Connection management and schema initialization
  - `QAList`: CRUD operations for QA lists
  - `QAItem`: Managing individual test items
  - `QAValidation`: Recording and retrieving validation results

- **Controllers** (`app.py`): Flask routes handling business logic
  - List management (create, view, publish, delete)
  - Item management (add, delete)
  - QA session management
  - Results viewing

- **Views** (`templates/`): HTML templates with Jinja2
  - List views (index, create, view)
  - QA session interface
  - Results dashboard

## Installation

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

### 4. Run QA Session

1. Go to "Published Lists"
2. Click "Start QA Session" on your list
3. For each item:
   - Read the description and expected result
   - Perform the test
   - Select status: Pass, Fail, Skip, or Blocked
   - Record actual result and any notes
   - Enter your name as validator
   - Click "Record Validation"
4. The app will auto-scroll to the next item

### 5. View Results

1. Click "View Results" from any list
2. See summary statistics (total, passed, failed, etc.)
3. Review detailed validation history
4. Use this to show stakeholders what was tested

## Database Schema

```sql
-- QA Lists
qa_lists (
    id, name, description, created_at, updated_at, is_published
)

-- QA Items (test cases)
qa_items (
    id, list_id, item_order, category, description, 
    expected_result, notes
)

-- QA Validations (results)
qa_validations (
    id, list_id, item_id, validated_at, status,
    actual_result, notes, validator_name
)
```

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

## Future Enhancements

- Test automation integration
- Jira/GitHub issue linking
- Email notifications for failures
- Test metrics and trends
- Screenshot attachments
- Multi-user support with roles

## License

Free to use and modify for your needs.
