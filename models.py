import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class Database:
    """Database connection manager"""
    
    def __init__(self, db_path: str = 'qa_tracker.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # QA Lists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_published BOOLEAN DEFAULT 0
            )
        ''')
        
        # QA Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                item_order INTEGER NOT NULL,
                category TEXT,
                description TEXT NOT NULL,
                expected_result TEXT,
                notes TEXT,
                FOREIGN KEY (list_id) REFERENCES qa_lists(id) ON DELETE CASCADE
            )
        ''')
        
        # QA Validations table (tracking actual QA work)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('pass', 'fail', 'skip', 'blocked')),
                actual_result TEXT,
                notes TEXT,
                validator_name TEXT,
                FOREIGN KEY (list_id) REFERENCES qa_lists(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES qa_items(id) ON DELETE CASCADE
            )
        ''')
        
        # QA Sessions table (group validations by session)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                session_name TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (list_id) REFERENCES qa_lists(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()


class QAList:
    """Model for QA Lists"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, name: str, description: str = None) -> int:
        """Create a new QA list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO qa_lists (name, description) VALUES (?, ?)',
            (name, description)
        )
        list_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return list_id
    
    def get_all(self, published_only: bool = False) -> List[Dict]:
        """Get all QA lists"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM qa_lists'
        if published_only:
            query += ' WHERE is_published = 1'
        query += ' ORDER BY updated_at DESC'
        
        cursor.execute(query)
        lists = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return lists
    
    def get_by_id(self, list_id: int) -> Optional[Dict]:
        """Get a specific QA list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM qa_lists WHERE id = ?', (list_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def publish(self, list_id: int):
        """Publish a QA list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE qa_lists SET is_published = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (list_id,)
        )
        conn.commit()
        conn.close()
    
    def unpublish(self, list_id: int):
        """Unpublish a QA list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE qa_lists SET is_published = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (list_id,)
        )
        conn.commit()
        conn.close()
    
    def delete(self, list_id: int):
        """Delete a QA list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM qa_lists WHERE id = ?', (list_id,))
        conn.commit()
        conn.close()


class QAItem:
    """Model for QA Items"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, list_id: int, description: str, category: str = None, 
               expected_result: str = None, notes: str = None) -> int:
        """Create a new QA item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get the next order number
        cursor.execute(
            'SELECT COALESCE(MAX(item_order), 0) + 1 FROM qa_items WHERE list_id = ?',
            (list_id,)
        )
        item_order = cursor.fetchone()[0]
        
        cursor.execute('''
            INSERT INTO qa_items (list_id, item_order, category, description, expected_result, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (list_id, item_order, category, description, expected_result, notes))
        
        item_id = cursor.lastrowid
        
        # Update list timestamp
        cursor.execute(
            'UPDATE qa_lists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (list_id,)
        )
        
        conn.commit()
        conn.close()
        return item_id
    
    def get_by_list(self, list_id: int) -> List[Dict]:
        """Get all items for a QA list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM qa_items WHERE list_id = ? ORDER BY item_order',
            (list_id,)
        )
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def update(self, item_id: int, **kwargs):
        """Update a QA item"""
        allowed_fields = ['category', 'description', 'expected_result', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [item_id]
        
        cursor.execute(f'UPDATE qa_items SET {set_clause} WHERE id = ?', values)
        conn.commit()
        conn.close()
    
    def delete(self, item_id: int):
        """Delete a QA item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM qa_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()


class QAValidation:
    """Model for QA Validations (tracking actual QA work)"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, list_id: int, item_id: int, status: str,
               actual_result: str = None, notes: str = None, 
               validator_name: str = None) -> int:
        """Record a validation"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO qa_validations (list_id, item_id, status, actual_result, notes, validator_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (list_id, item_id, status, actual_result, notes, validator_name))
        
        validation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return validation_id
    
    def get_by_list(self, list_id: int) -> List[Dict]:
        """Get all validations for a list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, i.description as item_description
            FROM qa_validations v
            JOIN qa_items i ON v.item_id = i.id
            WHERE v.list_id = ?
            ORDER BY v.validated_at DESC
        ''', (list_id,))
        
        validations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return validations
    
    def get_summary(self, list_id: int) -> Dict:
        """Get validation summary for a list"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_items,
                SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN status = 'fail' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'skip' THEN 1 ELSE 0 END) as skipped,
                SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END) as blocked
            FROM qa_validations
            WHERE list_id = ?
        ''', (list_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else {
            'total_items': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'blocked': 0
        }
