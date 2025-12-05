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

- **3 QA Lists** on the homepage:
  - Customer Data ETL Pipeline QA (published with some results)
  - User Registration Feature QA (published, ready to test)
  - SQL Query Performance Optimization QA (draft)

## Try It Out

### 1. View Existing List
- Click on "Customer Data ETL Pipeline QA"
- See 7 QA items organized by category
- Click "View Results" to see validation history

### 2. Run a QA Session
- Go to "Published Lists"
- Click "Start QA Session" on "User Registration Feature QA"
- Work through each item:
  - Read the test description
  - Perform the test (or simulate it)
  - Select Pass/Fail/Skip/Blocked
  - Add notes about what you found
  - Record validation

### 3. Create Your Own List
- Click "Create New List"
- Enter name: "My Data Pipeline QA"
- Add description: "Testing my ETL job"
- Click "Create List"
- Add items using "Add Item" button
- Publish when ready

## Key Features to Explore

✓ **List Management**: Create, view, publish, unpublish
✓ **Item Organization**: Categories, expected results, notes
✓ **QA Sessions**: Interactive validation workflow
✓ **Results Tracking**: Summary stats and detailed history
✓ **Status Options**: Pass, Fail, Skip, Blocked

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
