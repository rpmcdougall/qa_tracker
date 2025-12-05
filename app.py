from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import Database, QAList, QAItem, QAValidation
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Initialize database
db = Database()
qa_list_model = QAList(db)
qa_item_model = QAItem(db)
qa_validation_model = QAValidation(db)


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
    """View a QA list with all its items"""
    qa_list = qa_list_model.get_by_id(list_id)
    if not qa_list:
        flash('QA list not found', 'error')
        return redirect(url_for('index'))
    
    items = qa_item_model.get_by_list(list_id)
    return render_template('view_list.html', qa_list=qa_list, items=items)


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


# ===== QA VALIDATION ROUTES =====

@app.route('/published')
def published_lists():
    """View all published QA lists"""
    lists = qa_list_model.get_all(published_only=True)
    return render_template('published.html', lists=lists)


@app.route('/qa/<int:list_id>')
def qa_session(list_id):
    """Start a QA session for a published list"""
    qa_list = qa_list_model.get_by_id(list_id)
    if not qa_list:
        flash('QA list not found', 'error')
        return redirect(url_for('published_lists'))
    
    if not qa_list['is_published']:
        flash('This QA list is not published', 'error')
        return redirect(url_for('published_lists'))
    
    items = qa_item_model.get_by_list(list_id)
    return render_template('qa_session.html', qa_list=qa_list, items=items)


@app.route('/qa/<int:list_id>/validate', methods=['POST'])
def validate_item(list_id):
    """Record a validation for an item"""
    item_id = request.form.get('item_id')
    status = request.form.get('status')
    actual_result = request.form.get('actual_result')
    notes = request.form.get('notes')
    validator_name = request.form.get('validator_name')
    
    qa_validation_model.create(
        list_id, item_id, status, actual_result, notes, validator_name
    )
    
    return jsonify({'success': True})


@app.route('/list/<int:list_id>/results')
def view_results(list_id):
    """View QA results for a list"""
    qa_list = qa_list_model.get_by_id(list_id)
    if not qa_list:
        flash('QA list not found', 'error')
        return redirect(url_for('index'))
    
    validations = qa_validation_model.get_by_list(list_id)
    summary = qa_validation_model.get_summary(list_id)
    items = qa_item_model.get_by_list(list_id)
    
    return render_template('results.html', 
                         qa_list=qa_list, 
                         validations=validations,
                         summary=summary,
                         items=items)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
