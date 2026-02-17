"""
Database models for the chatbot
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Conversation(Base):
    """Store conversation sessions"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')
    

class Message(Base):
    """Store individual messages"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Feedback for learning
    feedback = Column(String(20), nullable=True)  # 'positive', 'negative', or None
    feedback_comment = Column(Text, nullable=True)
    
    # Source tracking (was it from Groq, RAG, or hybrid?)
    source = Column(String(50), nullable=True)
    
    # Relationships
    conversation = relationship('Conversation', back_populates='messages')


class TrainingDocument(Base):
    """Store training documents"""
    __tablename__ = 'training_documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=True)
    file_path = Column(String(500), nullable=True)
    
    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    
    # Categories/tags for organization
    category = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)  # JSON string of tags


class UserPreference(Base):
    """Store user preferences and context"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Preferences
    preferred_name = Column(String(100), nullable=True)
    language = Column(String(20), default='en')
    tone_preference = Column(String(50), nullable=True)  # 'formal', 'casual', 'technical'
    
    # Context
    interests = Column(Text, nullable=True)  # JSON string
    conversation_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntentPattern(Base):
    """Store learned intent patterns"""
    __tablename__ = 'intent_patterns'
    
    id = Column(Integer, primary_key=True)
    intent_name = Column(String(100), nullable=False, index=True)
    pattern = Column(String(500), nullable=False)
    confidence_threshold = Column(Float, default=0.7)
    
    # Response template
    response_template = Column(Text, nullable=True)
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db(database_url=None):
    """Initialize the database"""
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')
    
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return engine, Session


def get_session():
    """Get a database session"""
    _, Session = init_db()
    return Session()


if __name__ == '__main__':
    # Create all tables
    print("Creating database tables...")
    engine, _ = init_db()
    print("✓ Database tables created successfully!")
    print(f"✓ Database location: {os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')}")