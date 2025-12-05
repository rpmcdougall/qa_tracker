from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_URL, SQLALCHEMY_ENGINE_OPTIONS

# Create base class for declarative models
Base = declarative_base()

# Database engine and session
engine = create_engine(DATABASE_URL, **SQLALCHEMY_ENGINE_OPTIONS)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


# ORM Models
class QAListModel(Base):
    """QA List table"""
    __tablename__ = 'qa_lists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_published = Column(Boolean, default=False)
    
    # Relationships
    items = relationship("QAItemModel", back_populates="list", cascade="all, delete-orphan")
    validations = relationship("QAValidationModel", back_populates="list", cascade="all, delete-orphan")
    sessions = relationship("QASessionModel", back_populates="list", cascade="all, delete-orphan")


class QAItemModel(Base):
    """QA Item table"""
    __tablename__ = 'qa_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('qa_lists.id', ondelete='CASCADE'), nullable=False)
    item_order = Column(Integer, nullable=False)
    category = Column(String(100))
    description = Column(Text, nullable=False)
    expected_result = Column(Text)
    notes = Column(Text)
    
    # Relationships
    list = relationship("QAListModel", back_populates="items")
    validations = relationship("QAValidationModel", back_populates="item", cascade="all, delete-orphan")


class QAValidationModel(Base):
    """QA Validation table"""
    __tablename__ = 'qa_validations'
    __table_args__ = (
        CheckConstraint("status IN ('pass', 'fail', 'skip', 'blocked')", name='check_status'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('qa_lists.id', ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey('qa_items.id', ondelete='CASCADE'), nullable=False)
    validated_at = Column(DateTime, default=func.now())
    status = Column(String(20), nullable=False)
    actual_result = Column(Text)
    notes = Column(Text)
    validator_name = Column(String(100))
    
    # Relationships
    list = relationship("QAListModel", back_populates="validations")
    item = relationship("QAItemModel", back_populates="validations")


class QASessionModel(Base):
    """QA Session table"""
    __tablename__ = 'qa_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('qa_lists.id', ondelete='CASCADE'), nullable=False)
    session_name = Column(String(255), nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    list = relationship("QAListModel", back_populates="sessions")


class Database:
    """Database manager"""
    
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        Base.metadata.create_all(engine)
    
    def get_session(self):
        """Get a database session"""
        return Session()


class QAList:
    """Service class for QA Lists"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, name: str, description: str = None) -> int:
        """Create a new QA list"""
        session = self.db.get_session()
        try:
            qa_list = QAListModel(name=name, description=description)
            session.add(qa_list)
            session.commit()
            list_id = qa_list.id
            return list_id
        finally:
            session.close()
    
    def get_all(self, published_only: bool = False) -> List[Dict]:
        """Get all QA lists"""
        session = self.db.get_session()
        try:
            query = session.query(QAListModel)
            if published_only:
                query = query.filter(QAListModel.is_published == True)
            query = query.order_by(QAListModel.updated_at.desc())
            
            lists = []
            for qa_list in query.all():
                lists.append({
                    'id': qa_list.id,
                    'name': qa_list.name,
                    'description': qa_list.description,
                    'created_at': qa_list.created_at.strftime('%Y-%m-%d %H:%M:%S') if qa_list.created_at else None,
                    'updated_at': qa_list.updated_at.strftime('%Y-%m-%d %H:%M:%S') if qa_list.updated_at else None,
                    'is_published': qa_list.is_published
                })
            return lists
        finally:
            session.close()
    
    def get_by_id(self, list_id: int) -> Optional[Dict]:
        """Get a specific QA list"""
        session = self.db.get_session()
        try:
            qa_list = session.query(QAListModel).filter(QAListModel.id == list_id).first()
            if qa_list:
                return {
                    'id': qa_list.id,
                    'name': qa_list.name,
                    'description': qa_list.description,
                    'created_at': qa_list.created_at.strftime('%Y-%m-%d %H:%M:%S') if qa_list.created_at else None,
                    'updated_at': qa_list.updated_at.strftime('%Y-%m-%d %H:%M:%S') if qa_list.updated_at else None,
                    'is_published': qa_list.is_published
                }
            return None
        finally:
            session.close()
    
    def publish(self, list_id: int):
        """Publish a QA list"""
        session = self.db.get_session()
        try:
            qa_list = session.query(QAListModel).filter(QAListModel.id == list_id).first()
            if qa_list:
                qa_list.is_published = True
                qa_list.updated_at = func.now()
                session.commit()
        finally:
            session.close()
    
    def unpublish(self, list_id: int):
        """Unpublish a QA list"""
        session = self.db.get_session()
        try:
            qa_list = session.query(QAListModel).filter(QAListModel.id == list_id).first()
            if qa_list:
                qa_list.is_published = False
                qa_list.updated_at = func.now()
                session.commit()
        finally:
            session.close()
    
    def delete(self, list_id: int):
        """Delete a QA list"""
        session = self.db.get_session()
        try:
            qa_list = session.query(QAListModel).filter(QAListModel.id == list_id).first()
            if qa_list:
                session.delete(qa_list)
                session.commit()
        finally:
            session.close()


class QAItem:
    """Service class for QA Items"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, list_id: int, description: str, category: str = None, 
               expected_result: str = None, notes: str = None) -> int:
        """Create a new QA item"""
        session = self.db.get_session()
        try:
            # Get the next order number
            max_order = session.query(func.max(QAItemModel.item_order)).\
                filter(QAItemModel.list_id == list_id).scalar() or 0
            item_order = max_order + 1
            
            qa_item = QAItemModel(
                list_id=list_id,
                item_order=item_order,
                category=category,
                description=description,
                expected_result=expected_result,
                notes=notes
            )
            session.add(qa_item)
            
            # Update list timestamp
            qa_list = session.query(QAListModel).filter(QAListModel.id == list_id).first()
            if qa_list:
                qa_list.updated_at = func.now()
            
            session.commit()
            return qa_item.id
        finally:
            session.close()
    
    def get_by_list(self, list_id: int) -> List[Dict]:
        """Get all items for a QA list"""
        session = self.db.get_session()
        try:
            items = session.query(QAItemModel).\
                filter(QAItemModel.list_id == list_id).\
                order_by(QAItemModel.item_order).all()
            
            result = []
            for item in items:
                result.append({
                    'id': item.id,
                    'list_id': item.list_id,
                    'item_order': item.item_order,
                    'category': item.category,
                    'description': item.description,
                    'expected_result': item.expected_result,
                    'notes': item.notes
                })
            return result
        finally:
            session.close()
    
    def update(self, item_id: int, **kwargs):
        """Update a QA item"""
        allowed_fields = ['category', 'description', 'expected_result', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        session = self.db.get_session()
        try:
            qa_item = session.query(QAItemModel).filter(QAItemModel.id == item_id).first()
            if qa_item:
                for key, value in updates.items():
                    setattr(qa_item, key, value)
                session.commit()
        finally:
            session.close()
    
    def delete(self, item_id: int):
        """Delete a QA item"""
        session = self.db.get_session()
        try:
            qa_item = session.query(QAItemModel).filter(QAItemModel.id == item_id).first()
            if qa_item:
                session.delete(qa_item)
                session.commit()
        finally:
            session.close()


class QAValidation:
    """Service class for QA Validations (tracking actual QA work)"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, list_id: int, item_id: int, status: str,
               actual_result: str = None, notes: str = None, 
               validator_name: str = None) -> int:
        """Record a validation"""
        session = self.db.get_session()
        try:
            validation = QAValidationModel(
                list_id=list_id,
                item_id=item_id,
                status=status,
                actual_result=actual_result,
                notes=notes,
                validator_name=validator_name
            )
            session.add(validation)
            session.commit()
            return validation.id
        finally:
            session.close()
    
    def get_by_list(self, list_id: int) -> List[Dict]:
        """Get all validations for a list"""
        session = self.db.get_session()
        try:
            validations = session.query(
                QAValidationModel,
                QAItemModel.description.label('item_description')
            ).join(
                QAItemModel, QAValidationModel.item_id == QAItemModel.id
            ).filter(
                QAValidationModel.list_id == list_id
            ).order_by(
                QAValidationModel.validated_at.desc()
            ).all()
            
            result = []
            for validation, item_description in validations:
                result.append({
                    'id': validation.id,
                    'list_id': validation.list_id,
                    'item_id': validation.item_id,
                    'validated_at': validation.validated_at.strftime('%Y-%m-%d %H:%M:%S') if validation.validated_at else None,
                    'status': validation.status,
                    'actual_result': validation.actual_result,
                    'notes': validation.notes,
                    'validator_name': validation.validator_name,
                    'item_description': item_description
                })
            return result
        finally:
            session.close()
    
    def get_summary(self, list_id: int) -> Dict:
        """Get validation summary for a list"""
        session = self.db.get_session()
        try:
            from sqlalchemy import case
            
            summary = session.query(
                func.count(QAValidationModel.id).label('total_items'),
                func.sum(case((QAValidationModel.status == 'pass', 1), else_=0)).label('passed'),
                func.sum(case((QAValidationModel.status == 'fail', 1), else_=0)).label('failed'),
                func.sum(case((QAValidationModel.status == 'skip', 1), else_=0)).label('skipped'),
                func.sum(case((QAValidationModel.status == 'blocked', 1), else_=0)).label('blocked')
            ).filter(
                QAValidationModel.list_id == list_id
            ).first()
            
            return {
                'total_items': summary.total_items or 0,
                'passed': summary.passed or 0,
                'failed': summary.failed or 0,
                'skipped': summary.skipped or 0,
                'blocked': summary.blocked or 0
            }
        finally:
            session.close()
