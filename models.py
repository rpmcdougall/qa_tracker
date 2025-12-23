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
    """QA Validation table - Enhanced for phase tracking"""
    __tablename__ = 'qa_validations'
    __table_args__ = (
        CheckConstraint("status IN ('pass', 'fail', 'skip', 'blocked')", name='check_status'),
        CheckConstraint("phase IN (1, 2)", name='check_phase'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('qa_lists.id', ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey('qa_items.id', ondelete='CASCADE'))  # Nullable for Phase 2 items

    # Phase tracking fields
    session_id = Column(Integer, ForeignKey('qa_sessions.id', ondelete='CASCADE'), nullable=False)
    phase = Column(Integer, nullable=False)  # 1 or 2
    phase2_item_id = Column(Integer, ForeignKey('qa_session_phase2_items.id', ondelete='CASCADE'))  # For Phase 2 custom items

    validated_at = Column(DateTime, default=func.now())
    status = Column(String(20), nullable=False)
    actual_result = Column(Text)
    notes = Column(Text)
    validator_name = Column(String(100))

    # Relationships
    list = relationship("QAListModel", back_populates="validations")
    item = relationship("QAItemModel", back_populates="validations")
    session = relationship("QASessionModel", back_populates="validations")
    phase2_item = relationship("QASessionPhase2ItemModel", back_populates="validations")


class QASessionModel(Base):
    """QA Session table - Enhanced for two-phase tracking"""
    __tablename__ = 'qa_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('qa_lists.id', ondelete='CASCADE'), nullable=False)
    session_name = Column(String(255), nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    # Two-phase tracking fields
    current_phase = Column(Integer, default=1)
    phase1_started_at = Column(DateTime)
    phase1_completed_at = Column(DateTime)
    phase1_completed_by = Column(String(100))
    phase2_started_at = Column(DateTime)
    phase2_completed_at = Column(DateTime)
    phase2_completed_by = Column(String(100))

    # Relationships
    list = relationship("QAListModel", back_populates="sessions")
    validations = relationship("QAValidationModel", back_populates="session", cascade="all, delete-orphan")
    phase2_items = relationship("QASessionPhase2ItemModel", back_populates="session", cascade="all, delete-orphan")


class QATemplateModel(Base):
    """QA Template table - Reusable QA checklists"""
    __tablename__ = 'qa_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    items = relationship("QATemplateItemModel", back_populates="template", cascade="all, delete-orphan")


class QATemplateItemModel(Base):
    """QA Template Item table - Items within templates"""
    __tablename__ = 'qa_template_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey('qa_templates.id', ondelete='CASCADE'), nullable=False)
    item_order = Column(Integer, nullable=False)
    category = Column(String(100))
    description = Column(Text, nullable=False)
    expected_result = Column(Text)
    notes = Column(Text)

    # Relationships
    template = relationship("QATemplateModel", back_populates="items")


class QASessionPhase2ItemModel(Base):
    """QA Session Phase 2 Item table - Items added during Phase 2"""
    __tablename__ = 'qa_session_phase2_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('qa_sessions.id', ondelete='CASCADE'), nullable=False)
    item_order = Column(Integer, nullable=False)
    category = Column(String(100))
    description = Column(Text, nullable=False)
    expected_result = Column(Text)
    notes = Column(Text)
    source = Column(String(50))  # 'manual' or 'template'
    template_id = Column(Integer, ForeignKey('qa_templates.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    session = relationship("QASessionModel", back_populates="phase2_items")
    template = relationship("QATemplateModel")
    validations = relationship("QAValidationModel", back_populates="phase2_item", cascade="all, delete-orphan")


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
    """Service class for QA Validations (tracking actual QA work) - Enhanced for session/phase tracking"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, session_id: int, phase: int, list_id: int, status: str,
               item_id: int = None, phase2_item_id: int = None,
               actual_result: str = None, notes: str = None,
               validator_name: str = None) -> int:
        """Record a validation with phase tracking"""
        session = self.db.get_session()
        try:
            validation = QAValidationModel(
                session_id=session_id,
                phase=phase,
                list_id=list_id,
                item_id=item_id,
                phase2_item_id=phase2_item_id,
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
    
    def get_summary(self, list_id: int = None, session_id: int = None, phase: int = None) -> Dict:
        """Get validation summary for a list or session/phase"""
        session = self.db.get_session()
        try:
            from sqlalchemy import case

            query = session.query(
                func.count(QAValidationModel.id).label('total_items'),
                func.sum(case((QAValidationModel.status == 'pass', 1), else_=0)).label('passed'),
                func.sum(case((QAValidationModel.status == 'fail', 1), else_=0)).label('failed'),
                func.sum(case((QAValidationModel.status == 'skip', 1), else_=0)).label('skipped'),
                func.sum(case((QAValidationModel.status == 'blocked', 1), else_=0)).label('blocked')
            )

            if list_id:
                query = query.filter(QAValidationModel.list_id == list_id)
            if session_id:
                query = query.filter(QAValidationModel.session_id == session_id)
            if phase:
                query = query.filter(QAValidationModel.phase == phase)

            summary = query.first()

            return {
                'total_items': summary.total_items or 0,
                'passed': summary.passed or 0,
                'failed': summary.failed or 0,
                'skipped': summary.skipped or 0,
                'blocked': summary.blocked or 0
            }
        finally:
            session.close()

    def get_by_session(self, session_id: int, phase: int = None) -> List[Dict]:
        """Get validations for a session, optionally filtered by phase"""
        session = self.db.get_session()
        try:
            from sqlalchemy import case

            # Join with items to get descriptions (left join for phase2 items)
            query = session.query(
                QAValidationModel,
                QAItemModel.description.label('item_description'),
                QASessionPhase2ItemModel.description.label('phase2_item_description')
            ).outerjoin(
                QAItemModel, QAValidationModel.item_id == QAItemModel.id
            ).outerjoin(
                QASessionPhase2ItemModel, QAValidationModel.phase2_item_id == QASessionPhase2ItemModel.id
            ).filter(
                QAValidationModel.session_id == session_id
            )

            if phase:
                query = query.filter(QAValidationModel.phase == phase)

            query = query.order_by(QAValidationModel.validated_at.desc())

            result = []
            for validation, item_description, phase2_item_description in query.all():
                result.append({
                    'id': validation.id,
                    'session_id': validation.session_id,
                    'phase': validation.phase,
                    'item_id': validation.item_id,
                    'phase2_item_id': validation.phase2_item_id,
                    'validated_at': validation.validated_at.strftime('%Y-%m-%d %H:%M:%S') if validation.validated_at else None,
                    'status': validation.status,
                    'actual_result': validation.actual_result,
                    'notes': validation.notes,
                    'validator_name': validation.validator_name,
                    'item_description': phase2_item_description if phase2_item_description else item_description
                })
            return result
        finally:
            session.close()

    def get_by_session_grouped(self, session_id: int) -> Dict:
        """Get validations grouped by phase"""
        phase1_validations = self.get_by_session(session_id, phase=1)
        phase2_validations = self.get_by_session(session_id, phase=2)
        return {
            1: phase1_validations,
            2: phase2_validations
        }

    def get_timeline(self, session_id: int) -> List[Dict]:
        """Get chronological timeline of all validations"""
        return self.get_by_session(session_id)  # No phase filter, ordered by validated_at


class QASession:
    """Service class for QA Sessions with two-phase support"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, list_id: int, session_name: str) -> int:
        """Create a new QA session in Phase 1"""
        session = self.db.get_session()
        try:
            qa_session = QASessionModel(
                list_id=list_id,
                session_name=session_name,
                current_phase=1,
                phase1_started_at=func.now()
            )
            session.add(qa_session)
            session.commit()
            return qa_session.id
        finally:
            session.close()

    def get_by_id(self, session_id: int) -> Optional[Dict]:
        """Get session with all phase information"""
        session = self.db.get_session()
        try:
            qa_session = session.query(QASessionModel).filter(QASessionModel.id == session_id).first()
            if qa_session:
                return {
                    'id': qa_session.id,
                    'list_id': qa_session.list_id,
                    'session_name': qa_session.session_name,
                    'started_at': qa_session.started_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.started_at else None,
                    'completed_at': qa_session.completed_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.completed_at else None,
                    'current_phase': qa_session.current_phase,
                    'phase1_started_at': qa_session.phase1_started_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.phase1_started_at else None,
                    'phase1_completed_at': qa_session.phase1_completed_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.phase1_completed_at else None,
                    'phase1_completed_by': qa_session.phase1_completed_by,
                    'phase2_started_at': qa_session.phase2_started_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.phase2_started_at else None,
                    'phase2_completed_at': qa_session.phase2_completed_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.phase2_completed_at else None,
                    'phase2_completed_by': qa_session.phase2_completed_by
                }
            return None
        finally:
            session.close()

    def get_by_list(self, list_id: int) -> List[Dict]:
        """Get all sessions for a list"""
        session = self.db.get_session()
        try:
            sessions = session.query(QASessionModel).\
                filter(QASessionModel.list_id == list_id).\
                order_by(QASessionModel.started_at.desc()).all()

            result = []
            for qa_session in sessions:
                result.append({
                    'id': qa_session.id,
                    'list_id': qa_session.list_id,
                    'session_name': qa_session.session_name,
                    'started_at': qa_session.started_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.started_at else None,
                    'completed_at': qa_session.completed_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.completed_at else None,
                    'current_phase': qa_session.current_phase,
                    'phase1_completed_at': qa_session.phase1_completed_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.phase1_completed_at else None,
                    'phase1_completed_by': qa_session.phase1_completed_by,
                    'phase2_completed_at': qa_session.phase2_completed_at.strftime('%Y-%m-%d %H:%M:%S') if qa_session.phase2_completed_at else None,
                    'phase2_completed_by': qa_session.phase2_completed_by
                })
            return result
        finally:
            session.close()

    def complete_phase1(self, session_id: int, completed_by: str):
        """Mark Phase 1 as complete"""
        session = self.db.get_session()
        try:
            qa_session = session.query(QASessionModel).filter(QASessionModel.id == session_id).first()
            if qa_session:
                # Get the list to know how many items to check
                list_items_count = session.query(func.count(QAItemModel.id)).\
                    filter(QAItemModel.list_id == qa_session.list_id).scalar()

                # Count validations for Phase 1
                phase1_validations = session.query(func.count(func.distinct(QAValidationModel.item_id))).\
                    filter(
                        QAValidationModel.session_id == session_id,
                        QAValidationModel.phase == 1
                    ).scalar()

                if phase1_validations < list_items_count:
                    raise ValueError(f"Cannot complete Phase 1: Only {phase1_validations}/{list_items_count} items validated")

                qa_session.phase1_completed_at = func.now()
                qa_session.phase1_completed_by = completed_by
                session.commit()
        finally:
            session.close()

    def start_phase2(self, session_id: int) -> bool:
        """Start Phase 2 of the session"""
        session = self.db.get_session()
        try:
            qa_session = session.query(QASessionModel).filter(QASessionModel.id == session_id).first()
            if qa_session:
                if not qa_session.phase1_completed_at:
                    raise ValueError("Cannot start Phase 2: Phase 1 is not complete")

                qa_session.current_phase = 2
                qa_session.phase2_started_at = func.now()
                session.commit()
                return True
            return False
        finally:
            session.close()

    def complete_phase2(self, session_id: int, completed_by: str):
        """Mark Phase 2 as complete"""
        session = self.db.get_session()
        try:
            qa_session = session.query(QASessionModel).filter(QASessionModel.id == session_id).first()
            if qa_session:
                qa_session.phase2_completed_at = func.now()
                qa_session.phase2_completed_by = completed_by
                qa_session.completed_at = func.now()
                session.commit()
        finally:
            session.close()

    def get_items_for_phase(self, session_id: int, phase: int) -> List[Dict]:
        """Get all items for a specific phase"""
        session = self.db.get_session()
        try:
            qa_session = session.query(QASessionModel).filter(QASessionModel.id == session_id).first()
            if not qa_session:
                return []

            # Get original QA items
            original_items = session.query(QAItemModel).\
                filter(QAItemModel.list_id == qa_session.list_id).\
                order_by(QAItemModel.item_order).all()

            result = []
            for item in original_items:
                result.append({
                    'id': item.id,
                    'item_order': item.item_order,
                    'category': item.category,
                    'description': item.description,
                    'expected_result': item.expected_result,
                    'notes': item.notes,
                    'source': 'original'
                })

            # If Phase 2, also include Phase 2 custom items
            if phase == 2:
                phase2_items = session.query(QASessionPhase2ItemModel).\
                    filter(QASessionPhase2ItemModel.session_id == session_id).\
                    order_by(QASessionPhase2ItemModel.item_order).all()

                for item in phase2_items:
                    result.append({
                        'id': item.id,
                        'item_order': item.item_order,
                        'category': item.category,
                        'description': item.description,
                        'expected_result': item.expected_result,
                        'notes': item.notes,
                        'source': 'phase2',
                        'phase2_item_id': item.id
                    })

            return result
        finally:
            session.close()

    def can_start_phase2(self, session_id: int) -> tuple:
        """Check if Phase 2 can be started"""
        session = self.db.get_session()
        try:
            qa_session = session.query(QASessionModel).filter(QASessionModel.id == session_id).first()
            if not qa_session:
                return (False, "Session not found")

            if not qa_session.phase1_completed_at:
                return (False, "Phase 1 is not complete")

            return (True, "")
        finally:
            session.close()


class QATemplate:
    """Service class for QA Templates"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, name: str, description: str = None, category: str = None) -> int:
        """Create a new template"""
        session = self.db.get_session()
        try:
            template = QATemplateModel(
                name=name,
                description=description,
                category=category
            )
            session.add(template)
            session.commit()
            return template.id
        finally:
            session.close()

    def get_all(self, active_only: bool = True, category: str = None) -> List[Dict]:
        """Get all templates, optionally filtered"""
        session = self.db.get_session()
        try:
            query = session.query(QATemplateModel)
            if active_only:
                query = query.filter(QATemplateModel.is_active == True)
            if category:
                query = query.filter(QATemplateModel.category == category)
            query = query.order_by(QATemplateModel.name)

            templates = []
            for template in query.all():
                templates.append({
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'is_active': template.is_active,
                    'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S') if template.created_at else None,
                    'updated_at': template.updated_at.strftime('%Y-%m-%d %H:%M:%S') if template.updated_at else None
                })
            return templates
        finally:
            session.close()

    def get_by_id(self, template_id: int) -> Optional[Dict]:
        """Get template with items"""
        session = self.db.get_session()
        try:
            template = session.query(QATemplateModel).filter(QATemplateModel.id == template_id).first()
            if template:
                return {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'is_active': template.is_active,
                    'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S') if template.created_at else None,
                    'updated_at': template.updated_at.strftime('%Y-%m-%d %H:%M:%S') if template.updated_at else None
                }
            return None
        finally:
            session.close()

    def add_item(self, template_id: int, description: str, category: str = None,
                 expected_result: str = None, notes: str = None) -> int:
        """Add item to template"""
        session = self.db.get_session()
        try:
            # Get the next order number
            max_order = session.query(func.max(QATemplateItemModel.item_order)).\
                filter(QATemplateItemModel.template_id == template_id).scalar() or 0
            item_order = max_order + 1

            item = QATemplateItemModel(
                template_id=template_id,
                item_order=item_order,
                category=category,
                description=description,
                expected_result=expected_result,
                notes=notes
            )
            session.add(item)

            # Update template timestamp
            template = session.query(QATemplateModel).filter(QATemplateModel.id == template_id).first()
            if template:
                template.updated_at = func.now()

            session.commit()
            return item.id
        finally:
            session.close()

    def get_items(self, template_id: int) -> List[Dict]:
        """Get all items for a template"""
        session = self.db.get_session()
        try:
            items = session.query(QATemplateItemModel).\
                filter(QATemplateItemModel.template_id == template_id).\
                order_by(QATemplateItemModel.item_order).all()

            result = []
            for item in items:
                result.append({
                    'id': item.id,
                    'template_id': item.template_id,
                    'item_order': item.item_order,
                    'category': item.category,
                    'description': item.description,
                    'expected_result': item.expected_result,
                    'notes': item.notes
                })
            return result
        finally:
            session.close()


class QASessionPhase2Item:
    """Service class for Phase 2 custom items"""

    def __init__(self, db: Database):
        self.db = db

    def add_manual_item(self, session_id: int, description: str, category: str = None,
                        expected_result: str = None, notes: str = None) -> int:
        """Add a custom item during Phase 2"""
        session = self.db.get_session()
        try:
            # Get the next order number
            max_order = session.query(func.max(QASessionPhase2ItemModel.item_order)).\
                filter(QASessionPhase2ItemModel.session_id == session_id).scalar() or 0
            item_order = max_order + 1

            item = QASessionPhase2ItemModel(
                session_id=session_id,
                item_order=item_order,
                category=category,
                description=description,
                expected_result=expected_result,
                notes=notes,
                source='manual'
            )
            session.add(item)
            session.commit()
            return item.id
        finally:
            session.close()

    def import_from_template(self, session_id: int, template_id: int) -> int:
        """Import all items from a template"""
        session = self.db.get_session()
        try:
            # Get current max order
            max_order = session.query(func.max(QASessionPhase2ItemModel.item_order)).\
                filter(QASessionPhase2ItemModel.session_id == session_id).scalar() or 0

            # Get template items
            template_items = session.query(QATemplateItemModel).\
                filter(QATemplateItemModel.template_id == template_id).\
                order_by(QATemplateItemModel.item_order).all()

            count = 0
            for template_item in template_items:
                max_order += 1
                item = QASessionPhase2ItemModel(
                    session_id=session_id,
                    item_order=max_order,
                    category=template_item.category,
                    description=template_item.description,
                    expected_result=template_item.expected_result,
                    notes=template_item.notes,
                    source='template',
                    template_id=template_id
                )
                session.add(item)
                count += 1

            session.commit()
            return count
        finally:
            session.close()

    def get_by_session(self, session_id: int) -> List[Dict]:
        """Get all Phase 2 items for a session"""
        session = self.db.get_session()
        try:
            items = session.query(QASessionPhase2ItemModel).\
                filter(QASessionPhase2ItemModel.session_id == session_id).\
                order_by(QASessionPhase2ItemModel.item_order).all()

            result = []
            for item in items:
                result.append({
                    'id': item.id,
                    'session_id': item.session_id,
                    'item_order': item.item_order,
                    'category': item.category,
                    'description': item.description,
                    'expected_result': item.expected_result,
                    'notes': item.notes,
                    'source': item.source,
                    'template_id': item.template_id,
                    'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else None
                })
            return result
        finally:
            session.close()
