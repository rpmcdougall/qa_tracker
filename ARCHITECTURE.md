# QA Tracker Architecture Overview

## MVC Pattern Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                        │
│                  (Interacts via HTTP requests)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION                        │
│                       (app.py)                              │
├─────────────────────────────────────────────────────────────┤
│                      CONTROLLERS                            │
│  Routes handle HTTP requests and coordinate between         │
│  models and views                                           │
│                                                             │
│  • GET  /                  → index()                        │
│  • GET  /list/create       → create_list()                  │
│  • POST /list/create       → create_list()                  │
│  • GET  /list/<id>         → view_list()                    │
│  • POST /list/<id>/publish → publish_list()                 │
│  • GET  /qa/<id>           → qa_session()                   │
│  • POST /qa/<id>/validate  → validate_item()                │
│  • GET  /list/<id>/results → view_results()                 │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
    ┌────────────────┐          ┌──────────────────┐
    │     MODELS     │          │      VIEWS       │
    │   (models.py)  │          │   (templates/)   │
    ├────────────────┤          ├──────────────────┤
    │  Data Layer    │          │  Presentation    │
    │                │          │                  │
    │ • Database     │          │ • base.html      │
    │ • QAList       │          │ • index.html     │
    │ • QAItem       │          │ • view_list.html │
    │ • QAValidation │          │ • qa_session.html│
    │                │          │ • results.html   │
    └───────┬────────┘          │ • + more         │
            │                   └──────────────────┘
            ▼
    ┌────────────────┐
    │  SQLite DB     │
    │ qa_tracker.db  │
    ├────────────────┤
    │ • qa_lists     │
    │ • qa_items     │
    │ • qa_validations│
    │ • qa_sessions  │
    └────────────────┘
```

## Component Responsibilities

### Models (Data Layer)
**File**: `models.py`

Handles all database operations:
- Database connection management
- Schema initialization
- CRUD operations for QA lists, items, and validations
- Business logic for data integrity

**Key Classes**:
- `Database`: Connection pooling and schema setup
- `QAList`: Manages QA list lifecycle (create, publish, delete)
- `QAItem`: Handles test items within lists
- `QASession`: Two-phase workflow management (Phase 1 → Phase 2)
- `QAValidation`: Records and retrieves validation results by phase
- `QATemplate`: Manages reusable QA checklist templates
- `QASessionPhase2Item`: Handles custom items added during Phase 2

### Controllers (Business Logic)
**File**: `app.py`

Coordinates between models and views:
- Processes HTTP requests
- Validates user input
- Calls appropriate model methods
- Selects and renders templates
- Handles errors and flash messages

**Route Groups**:
- List Management: Create, view, publish, delete lists
- Item Management: Add, delete, and reorder test items
- Session Management: Create sessions, manage Phase 1/2 workflow, complete phases
- Template Management: Create templates, add template items
- Phase 2 Item Management: Add custom items, import from templates
- QA Validation: Record validations for Phase 1 and Phase 2
- Results: View separate Phase 1, Phase 2, and Timeline results

### Views (Presentation Layer)
**Directory**: `templates/`

HTML templates with Jinja2:
- Display data from controllers
- Provide user interaction forms
- Maintain consistent UI across pages
- Handle dynamic content rendering

**Template Structure**:
- `base.html`: Common layout and navigation
- Feature templates: Specific page layouts
- Includes: Reusable components

## Data Flow Example

### Creating a QA List

```
1. User clicks "Create New List"
   ↓
2. Controller serves create_list.html template
   ↓
3. User fills form and submits
   ↓
4. Controller receives POST request
   ↓
5. Controller validates input
   ↓
6. Controller calls QAList.create(name, description)
   ↓
7. Model inserts record into database
   ↓
8. Model returns new list_id
   ↓
9. Controller redirects to view_list page
   ↓
10. View displays the new QA list
```

### Running a Two-Phase QA Session

```
Phase 1 (Developer QA):
1. User creates session for published list
   ↓
2. Controller calls QASession.create() → starts in Phase 1
   ↓
3. User validates each item via /qa/<session_id>/phase/1
   ↓
4. JavaScript sends AJAX POST to /qa/<session_id>/validate with phase=1
   ↓
5. Controller calls QAValidation.create(session_id, phase=1, ...)
   ↓
6. User completes all items, clicks "Complete Phase 1"
   ↓
7. Controller calls QASession.complete_phase1()
   ↓
8. Model verifies all items validated, updates phase1_completed_at

Phase 2 (QA Engineer Review):
9. User clicks "Start Phase 2"
   ↓
10. Controller calls QASession.start_phase2()
   ↓
11. Model updates current_phase=2, phase2_started_at
   ↓
12. User validates items via /qa/<session_id>/phase/2
    ↓
13. User adds custom item via /session/<id>/add-item
    ↓
14. Controller calls QASessionPhase2Item.add_manual_item()
    ↓
15. User imports template via /session/<id>/import-template
    ↓
16. Controller calls QASessionPhase2Item.import_from_template()
    ↓
17. User validates all items (original + custom)
    ↓
18. User clicks "Complete Phase 2"
    ↓
19. Controller calls QASession.complete_phase2()
    ↓
20. Model updates phase2_completed_at

Results View:
21. User navigates to /session/<id>/results
    ↓
22. Controller fetches validations grouped by phase
    ↓
23. View renders three tabs: Phase 1, Phase 2, Timeline
    ↓
24. Each tab shows relevant validations and summaries
```

## File Structure

```
qa_tracker/
│
├── app.py                      # Flask app and controllers (routes)
├── models.py                   # Data models and database logic
├── config.py                   # Database configuration
├── requirements.txt            # Python dependencies
├── sample_data.py             # Script to create sample data
├── test_setup.py              # Automated test setup and validation
│
├── templates/                 # HTML templates (views)
│   ├── base.html              # Base layout with navigation
│   ├── index.html             # Homepage
│   ├── create_list.html       # Create QA list form
│   ├── view_list.html         # View list with items and sessions
│   ├── add_item.html          # Add item form
│   ├── published.html         # Published lists with sessions
│   ├── start_session.html     # Create new session form
│   ├── qa_session_phase.html  # Phase 1 or Phase 2 QA interface
│   ├── session_results.html   # Three-tab results view
│   └── templates_manage.html  # Template management interface
│
├── static/                    # CSS, JS, images
│   └── css/
│       └── style.css          # Comprehensive styling with phase UI
│
├── tests/                     # Test suite
│   ├── test_models.py         # Model unit tests
│   └── test_api.py            # API endpoint tests
│
├── qa_tracker.db             # SQLite database (created on first run)
│
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
├── ARCHITECTURE.md           # This file
├── TESTING.md                # Comprehensive testing guide
├── CHANGES.md                # Changelog
├── DATABASE_SETUP.md         # Database backend setup guide
└── DATABASE_QUICK_REF.md     # Database quick reference
```

## Technology Stack

- **Backend**: Python 3.x + Flask 3.0
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite 3 (default), PostgreSQL, MySQL, Snowflake, or Databricks
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Template Engine**: Jinja2
- **Architecture**: MVC (Model-View-Controller)

## Key Design Decisions

### Why SQLite?
- Zero configuration
- Single file database
- Perfect for small to medium workloads
- Easy to backup and share
- No separate database server needed

### Why Flask?
- Lightweight and fast
- Easy to understand
- Great for MVC pattern
- Excellent documentation
- Python-based (matches data engineering stack)

### Why No JavaScript Framework?
- Keeps it simple and dependency-free
- Vanilla JS is sufficient for the interactions needed
- Easier to understand and modify
- No build process required

## Security Considerations

Current implementation is for single-user or trusted network use. For production:

1. Add authentication (Flask-Login)
2. Implement CSRF protection
3. Add input sanitization
4. Use environment variables for secrets
5. Add rate limiting
6. Implement proper session management
7. Use HTTPS in production

## Performance Considerations

SQLite is suitable for:
- Single user or small team (5-10 concurrent users)
- Read-heavy workloads
- Small to medium datasets (< 1GB)

For larger scale:
- Migrate to PostgreSQL or MySQL
- Add caching (Redis)
- Implement connection pooling
- Add pagination for large lists

## Extension Points

Easy places to extend functionality:

1. **Custom Status Types**: Modify `qa_validations.status` CHECK constraint
2. ~~**Item Templates**: Add common test patterns to speed up list creation~~ ✅ **Implemented**
3. ~~**Session Tracking**: Group validations by date/time sessions~~ ✅ **Implemented**
4. **Export/Import**: Add JSON/CSV export of lists and results
5. **Screenshots**: Attach images to validation results
6. **Test Automation**: Link automated test runs to QA items
7. **Notifications**: Email alerts for phase completions
8. **Analytics**: Dashboard with trends and metrics over time
9. **API**: RESTful API for integration with CI/CD
10. **User Authentication**: Flask-Login for multi-user support with roles

## Testing Strategy

Implemented testing approach:

1. **Model Unit Tests** (`tests/test_models.py`): 50+ tests covering all service classes
   - Database, QAList, QAItem, QASession, QAValidation, QATemplate, QASessionPhase2Item
   - Comprehensive coverage of CRUD operations, phase transitions, validations
2. **API Integration Tests** (`tests/test_api.py`): 40+ tests covering all Flask routes
   - Session management, Phase 1/2 workflow, template management
   - Phase 2 item operations, validation recording, results display
3. **Automated Setup Test** (`test_setup.py`): End-to-end workflow validation
   - Database initialization, sample data creation, complete two-phase workflow
4. **Manual Testing**: Comprehensive guide in `TESTING.md`

Run tests with:
```bash
python test_setup.py                   # Quick setup validation
python -m unittest discover tests      # Full test suite
python -m unittest tests.test_models   # Model tests only
python -m unittest tests.test_api      # API tests only
```

## Deployment Options

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker
Create a Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Cloud Platforms
- Heroku: One-click deploy
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service

---

This architecture provides a solid foundation for a QA tracking system while remaining simple enough to understand and modify for your specific needs.
