from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import Database, QAList, QAItem, QAValidation, QASession, QATemplate, QASessionPhase2Item
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Initialize database
db = Database()
qa_list_model = QAList(db)
qa_item_model = QAItem(db)
qa_validation_model = QAValidation(db)
qa_session_model = QASession(db)
qa_template_model = QATemplate(db)
qa_phase2_item_model = QASessionPhase2Item(db)


# ===== LIST MANAGEMENT ROUTES =====

@app.route('/')
def index():
    """Homepage - show all QA lists"""
    lists = qa_list_model.get_all()
    return render_template('index.html', lists=lists)


@app.route('/list/create', methods=['GET', 'POST'])
def create_list():
    """Create a new QA list"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('List name is required', 'error')
            return render_template('create_list.html')
        
        list_id = qa_list_model.create(name, description)
        flash(f'QA list "{name}" created successfully', 'success')
        return redirect(url_for('view_list', list_id=list_id))
    
    return render_template('create_list.html')


@app.route('/list/<int:list_id>')
def view_list(list_id):
    """View a QA list with all its items and sessions"""
    qa_list = qa_list_model.get_by_id(list_id)
    if not qa_list:
        flash('QA list not found', 'error')
        return redirect(url_for('index'))

    items = qa_item_model.get_by_list(list_id)
    sessions = qa_session_model.get_by_list(list_id)
    return render_template('view_list.html', qa_list=qa_list, items=items, sessions=sessions)


@app.route('/list/<int:list_id>/publish', methods=['POST'])
def publish_list(list_id):
    """Publish a QA list"""
    qa_list_model.publish(list_id)
    flash('QA list published successfully', 'success')
    return redirect(url_for('view_list', list_id=list_id))


@app.route('/list/<int:list_id>/unpublish', methods=['POST'])
def unpublish_list(list_id):
    """Unpublish a QA list"""
    qa_list_model.unpublish(list_id)
    flash('QA list unpublished', 'success')
    return redirect(url_for('view_list', list_id=list_id))


@app.route('/list/<int:list_id>/delete', methods=['POST'])
def delete_list(list_id):
    """Delete a QA list"""
    qa_list_model.delete(list_id)
    flash('QA list deleted', 'success')
    return redirect(url_for('index'))


# ===== ITEM MANAGEMENT ROUTES =====

@app.route('/list/<int:list_id>/item/add', methods=['GET', 'POST'])
def add_item(list_id):
    """Add a new item to a QA list"""
    qa_list = qa_list_model.get_by_id(list_id)
    if not qa_list:
        flash('QA list not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        description = request.form.get('description')
        category = request.form.get('category')
        expected_result = request.form.get('expected_result')
        notes = request.form.get('notes')
        
        if not description:
            flash('Item description is required', 'error')
            return render_template('add_item.html', qa_list=qa_list)
        
        qa_item_model.create(list_id, description, category, expected_result, notes)
        flash('QA item added successfully', 'success')
        return redirect(url_for('view_list', list_id=list_id))
    
    return render_template('add_item.html', qa_list=qa_list)


@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete a QA item"""
    list_id = request.form.get('list_id')
    qa_item_model.delete(item_id)
    flash('QA item deleted', 'success')
    return redirect(url_for('view_list', list_id=list_id))


# ===== SESSION MANAGEMENT ROUTES =====

@app.route('/list/<int:list_id>/session/create', methods=['GET', 'POST'])
def create_session(list_id):
    """Create a new QA session"""
    qa_list = qa_list_model.get_by_id(list_id)
    if not qa_list:
        flash('QA list not found', 'error')
        return redirect(url_for('index'))

    if not qa_list['is_published']:
        flash('QA list must be published to create a session', 'error')
        return redirect(url_for('view_list', list_id=list_id))

    if request.method == 'POST':
        session_name = request.form.get('session_name')

        if not session_name:
            flash('Session name is required', 'error')
            return render_template('start_session.html', qa_list=qa_list)

        session_id = qa_session_model.create(list_id, session_name)
        flash(f'QA session "{session_name}" created successfully', 'success')
        return redirect(url_for('qa_session_phase', session_id=session_id, phase=1))

    return render_template('start_session.html', qa_list=qa_list)


@app.route('/session/<int:session_id>')
def view_session(session_id):
    """View session details"""
    session = qa_session_model.get_by_id(session_id)
    if not session:
        flash('Session not found', 'error')
        return redirect(url_for('published_lists'))

    qa_list = qa_list_model.get_by_id(session['list_id'])
    return render_template('session_details.html', session=session, qa_list=qa_list)


@app.route('/session/<int:session_id>/complete-phase1', methods=['POST'])
def complete_phase1(session_id):
    """Complete Phase 1 of a session"""
    completed_by = request.form.get('completed_by')

    if not completed_by:
        flash('Please enter your name', 'error')
        return redirect(url_for('qa_session_phase', session_id=session_id, phase=1))

    try:
        qa_session_model.complete_phase1(session_id, completed_by)
        flash('Phase 1 completed successfully! Phase 2 is now available.', 'success')
        return redirect(url_for('published_lists'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('qa_session_phase', session_id=session_id, phase=1))


@app.route('/session/<int:session_id>/start-phase2', methods=['POST'])
def start_phase2(session_id):
    """Start Phase 2 of a session"""
    try:
        qa_session_model.start_phase2(session_id)
        flash('Phase 2 started successfully!', 'success')
        return redirect(url_for('qa_session_phase', session_id=session_id, phase=2))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('published_lists'))


@app.route('/session/<int:session_id>/complete-phase2', methods=['POST'])
def complete_phase2(session_id):
    """Complete Phase 2 of a session"""
    completed_by = request.form.get('completed_by')

    if not completed_by:
        flash('Please enter your name', 'error')
        return redirect(url_for('qa_session_phase', session_id=session_id, phase=2))

    qa_session_model.complete_phase2(session_id, completed_by)
    flash('Phase 2 and session completed successfully!', 'success')
    return redirect(url_for('session_results', session_id=session_id))


# ===== PHASE 2 ITEM MANAGEMENT ROUTES =====

@app.route('/session/<int:session_id>/add-item', methods=['POST'])
def add_phase2_item(session_id):
    """Add a custom item during Phase 2"""
    description = request.form.get('description')
    category = request.form.get('category')
    expected_result = request.form.get('expected_result')
    notes = request.form.get('notes')

    if not description:
        return jsonify({'success': False, 'error': 'Description is required'})

    try:
        item_id = qa_phase2_item_model.add_manual_item(
            session_id, description, category, expected_result, notes
        )
        return jsonify({'success': True, 'item_id': item_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/session/<int:session_id>/import-template', methods=['POST'])
def import_template(session_id):
    """Import items from a template into Phase 2"""
    template_id = request.form.get('template_id')

    if not template_id:
        flash('Please select a template', 'error')
        return redirect(url_for('qa_session_phase', session_id=session_id, phase=2))

    try:
        count = qa_phase2_item_model.import_from_template(session_id, int(template_id))
        flash(f'{count} items imported from template successfully', 'success')
    except Exception as e:
        flash(f'Error importing template: {str(e)}', 'error')

    return redirect(url_for('qa_session_phase', session_id=session_id, phase=2))


# ===== TEMPLATE MANAGEMENT ROUTES =====

@app.route('/templates')
def list_templates():
    """List all available templates"""
    templates = qa_template_model.get_all()
    return render_template('templates_list.html', templates=templates)


@app.route('/templates/manage')
def manage_templates():
    """Template management page"""
    templates = qa_template_model.get_all(active_only=False)
    return render_template('templates_manage.html', templates=templates)


@app.route('/template/create', methods=['POST'])
def create_template():
    """Create a new template"""
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')

    if not name:
        flash('Template name is required', 'error')
        return redirect(url_for('manage_templates'))

    template_id = qa_template_model.create(name, description, category)
    flash(f'Template "{name}" created successfully', 'success')
    return redirect(url_for('manage_templates'))


@app.route('/template/<int:template_id>/add-item', methods=['POST'])
def add_template_item(template_id):
    """Add item to a template"""
    description = request.form.get('description')
    category = request.form.get('category')
    expected_result = request.form.get('expected_result')
    notes = request.form.get('notes')

    if not description:
        flash('Item description is required', 'error')
        return redirect(url_for('manage_templates'))

    qa_template_model.add_item(template_id, description, category, expected_result, notes)
    flash('Template item added successfully', 'success')
    return redirect(url_for('manage_templates'))


# ===== QA VALIDATION ROUTES =====

@app.route('/published')
def published_lists():
    """View all published QA lists with their sessions"""
    lists = qa_list_model.get_all(published_only=True)

    # Get sessions for each list
    for qa_list in lists:
        qa_list['sessions'] = qa_session_model.get_by_list(qa_list['id'])

    return render_template('published.html', lists=lists)


@app.route('/qa/<int:session_id>/phase/<int:phase>')
def qa_session_phase(session_id, phase):
    """Conduct QA for a specific phase of a session"""
    session = qa_session_model.get_by_id(session_id)
    if not session:
        flash('Session not found', 'error')
        return redirect(url_for('published_lists'))

    # Check phase is valid
    if phase not in [1, 2]:
        flash('Invalid phase', 'error')
        return redirect(url_for('published_lists'))

    # For Phase 2, check that Phase 1 is complete
    if phase == 2:
        can_start, reason = qa_session_model.can_start_phase2(session_id)
        if not can_start:
            flash(reason, 'error')
            return redirect(url_for('published_lists'))

    qa_list = qa_list_model.get_by_id(session['list_id'])
    items = qa_session_model.get_items_for_phase(session_id, phase)

    # Get templates for Phase 2
    templates = []
    if phase == 2:
        templates = qa_template_model.get_all()

    return render_template('qa_session_phase.html',
                         session=session,
                         qa_list=qa_list,
                         items=items,
                         phase=phase,
                         templates=templates)


@app.route('/qa/<int:session_id>/validate', methods=['POST'])
def validate_item_session(session_id):
    """Record a validation for an item in a session"""
    session = qa_session_model.get_by_id(session_id)
    if not session:
        return jsonify({'success': False, 'error': 'Session not found'})

    phase = int(request.form.get('phase'))
    item_id = request.form.get('item_id')
    phase2_item_id = request.form.get('phase2_item_id')
    status = request.form.get('status')
    actual_result = request.form.get('actual_result')
    notes = request.form.get('notes')
    validator_name = request.form.get('validator_name')

    try:
        qa_validation_model.create(
            session_id=session_id,
            phase=phase,
            list_id=session['list_id'],
            item_id=int(item_id) if item_id else None,
            phase2_item_id=int(phase2_item_id) if phase2_item_id else None,
            status=status,
            actual_result=actual_result,
            notes=notes,
            validator_name=validator_name
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/session/<int:session_id>/results')
def session_results(session_id):
    """View QA results for a session with phase tabs"""
    session = qa_session_model.get_by_id(session_id)
    if not session:
        flash('Session not found', 'error')
        return redirect(url_for('published_lists'))

    qa_list = qa_list_model.get_by_id(session['list_id'])

    # Get validations grouped by phase
    validations_grouped = qa_validation_model.get_by_session_grouped(session_id)
    timeline = qa_validation_model.get_timeline(session_id)

    # Get summaries for each phase
    summary_phase1 = qa_validation_model.get_summary(session_id=session_id, phase=1)
    summary_phase2 = qa_validation_model.get_summary(session_id=session_id, phase=2)
    summary_overall = qa_validation_model.get_summary(session_id=session_id)

    # Get items
    items = qa_item_model.get_by_list(session['list_id'])
    phase2_items = qa_phase2_item_model.get_by_session(session_id)

    return render_template('session_results.html',
                         session=session,
                         qa_list=qa_list,
                         validations_phase1=validations_grouped[1],
                         validations_phase2=validations_grouped[2],
                         timeline=timeline,
                         summary_phase1=summary_phase1,
                         summary_phase2=summary_phase2,
                         summary_overall=summary_overall,
                         items=items,
                         phase2_items=phase2_items)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
