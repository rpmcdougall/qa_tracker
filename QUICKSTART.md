# Quick Start Guide - QA Tracker

## Setup (5 minutes)

1. **Download the files** to your local machine

2. **Navigate to the directory**:
   ```bash
   cd qa_tracker
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Load sample data** (optional but recommended):
   ```bash
   python sample_data.py
   ```

5. **Start the application**:
   ```bash
   python app.py
   ```

6. **Open in browser**:
   Go to `http://localhost:5000`

## What You'll See

With sample data loaded, you'll see:

- **QA Lists** on the homepage (draft and published)
- **Published Lists** with session management
- **Two-Phase QA Workflow**: Developer validation (Phase 1) → QA Engineer review (Phase 2)
- **Template Management**: Reusable QA checklists
- **Results Display**: Three-tab interface showing Phase 1, Phase 2, and Timeline

## Try It Out

### 1. View Existing Lists
- Browse your QA lists on the homepage
- Click on any list to view items and sessions
- See session history and status (Phase 1, Phase 2, Completed)

### 2. Create and Run a Two-Phase QA Session
**Phase 1 - Developer QA:**
- Go to "Published Lists"
- Click "Create New Session" on any published list
- Enter session name (e.g., "Sprint 24 Testing")
- Validate each item:
  - Select Pass/Fail/Skip/Blocked
  - Record actual results and notes
  - Enter your name as validator
- Click "Complete Phase 1" when all items are validated

**Phase 2 - QA Engineer Review:**
- Click "Start Phase 2" on the session
- Re-validate original items (separate from Phase 1)
- Add custom test items using "+ Add Custom Item"
- Import items from templates (if available)
- Complete all validations
- Click "Complete Phase 2"

### 3. View Results
- Navigate to any session
- Click "View Results"
- Explore three tabs:
  - **Phase 1 Results**: Developer validation summary
  - **Phase 2 Results**: QA Engineer findings + custom items
  - **Timeline**: Chronological view of all validations

### 4. Create Templates (Optional)
- Navigate to "Manage Templates"
- Create reusable checklists (e.g., "Security Checklist")
- Add items to templates
- Import template items during Phase 2 of any session

### 5. Create Your Own List
- Click "Create New List"
- Enter name: "My Data Pipeline QA"
- Add description: "Testing my ETL job"
- Add items with categories and expected results
- Publish when ready
- Create sessions to start the two-phase QA workflow

## Key Features to Explore

✓ **List Management**: Create, view, publish, unpublish
✓ **Item Organization**: Categories, expected results, notes, reordering
✓ **Two-Phase QA Workflow**: Developer QA (Phase 1) → QA Engineer Review (Phase 2)
✓ **Session Management**: Create named sessions, track progress over time
✓ **Phase 2 Customization**: Add custom items, import from templates
✓ **Template System**: Create and manage reusable QA checklists
✓ **Results Tracking**: Three-tab view (Phase 1, Phase 2, Timeline) with summary stats
✓ **Status Options**: Pass, Fail, Skip, Blocked
✓ **Independent Validations**: Same item can have different results in Phase 1 and Phase 2

## Common Use Cases

### For Data Engineering Work:
- ETL pipeline validation
- Data quality checks
- Schema migration testing
- Performance benchmarking

### For Development Work:
- Feature acceptance testing
- Bug fix verification
- Regression testing
- Integration testing

## Next Steps

1. Delete sample data if desired (delete the .db file)
2. Create lists for your real work
3. Share published lists with your team
4. Use results to document your QA work

## Tips

- **One Test Per Item**: Keep items focused on a single test
- **Clear Expected Results**: Define what success looks like
- **Use Categories**: Group related tests (Functionality, Performance, etc.)
- **Add Context in Notes**: Include prerequisites or test data info
- **Record Everything**: Even skipped tests are valuable documentation

## Database Location

The SQLite database is created as `qa_tracker.db` in the application directory. 
You can:
- Back it up by copying the file
- Reset by deleting the file (it will be recreated on next run)
- Move it to a shared location for team access

## Need Help?

See the full README.md for:
- Detailed architecture explanation
- Database schema
- Extension ideas
- Troubleshooting tips

---

**That's it! You're ready to track your QA work.**
