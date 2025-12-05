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
- `QAValidation`: Records and retrieves validation results

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
- Item Management: Add and delete test items
- QA Sessions: Conduct validation sessions
- Results: View validation history and summaries

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

### Running a QA Session

```
1. User navigates to published list
   ↓
2. Controller fetches list and items via models
   ↓
3. View renders qa_session.html with data
   ↓
4. User completes validation for an item
   ↓
5. JavaScript sends AJAX POST to /qa/<id>/validate
   ↓
6. Controller receives validation data
   ↓
7. Controller calls QAValidation.create()
   ↓
8. Model inserts validation record
   ↓
9. Controller returns success JSON
   ↓
10. JavaScript updates UI, scrolls to next item
```

## File Structure

```
qa_tracker/
│
├── app.py                 # Flask app and controllers (routes)
├── models.py              # Data models and database logic
├── requirements.txt       # Python dependencies
├── sample_data.py        # Script to create sample data
│
├── templates/            # HTML templates (views)
│   ├── base.html
│   ├── index.html
│   ├── create_list.html
│   ├── view_list.html
│   ├── add_item.html
│   ├── published.html
│   ├── qa_session.html
│   └── results.html
│
├── static/               # CSS, JS, images
│   └── css/
│       └── style.css
│
├── qa_tracker.db        # SQLite database (created on first run)
│
├── README.md            # Full documentation
├── QUICKSTART.md        # Quick start guide
└── ARCHITECTURE.md      # This file
```

## Technology Stack

- **Backend**: Python 3.x + Flask 3.0
- **Database**: SQLite 3
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
2. **Item Templates**: Add common test patterns to speed up list creation
3. **Export/Import**: Add JSON/CSV export of lists and results
4. **Screenshots**: Attach images to validation results
5. **Test Automation**: Link automated test runs to QA items
6. **Notifications**: Email alerts for failed validations
7. **Analytics**: Dashboard with trends and metrics
8. **API**: RESTful API for integration with CI/CD

## Testing Strategy

Recommended testing approach:

1. **Unit Tests**: Test model methods independently
2. **Integration Tests**: Test route handlers with test database
3. **UI Tests**: Selenium or Playwright for end-to-end flows
4. **Manual Testing**: Use sample_data.py to verify features

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
