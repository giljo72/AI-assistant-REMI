# src/db/models.py
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Boolean, Float, JSON, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import datetime
import sqlalchemy.dialects.postgresql as pg

Base = declarative_base()

class Document(Base):
    """Document metadata model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    tag = Column(String, nullable=False)  # P, B, or PB
    description = Column(Text)
    status = Column(String, nullable=False)  # Active, Detached, Failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    chunk_count = Column(Integer, default=0)
    processing_error = Column(Text)
    
    # Relationships
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")
    project_associations = relationship("DocumentProject", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_tag', 'tag'),
        Index('idx_documents_status', 'status'),
    )

class DocumentEmbedding(Base):
    """Vector embeddings for document chunks"""
    __tablename__ = "document_embeddings"
    
    id = Column(Integer, primary_key=True)
    content_hash = Column(String, unique=True, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  # OpenAI embedding size
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    
    # Additional fields for context
    chunk_index = Column(Integer, nullable=False)  # Position in the document
    chunk_text = Column(Text, nullable=False)      # Actual text of the chunk
    chunk_metadata = Column(JSON)                  # Optional metadata
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    
    # Indexes
    __table_args__ = (
        Index('idx_document_embeddings_document_id', 'document_id'),
    )

class Project(Base):
    """Project model to organize related documents and chats"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    custom_prompt = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    chats = relationship("Chat", back_populates="project", cascade="all, delete-orphan")
    document_associations = relationship("DocumentProject", back_populates="project", cascade="all, delete-orphan")

class Chat(Base):
    """Chat model for conversations within a project"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_chats_project_id', 'project_id'),
    )

class Message(Base):
    """Message model for chat history"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_messages_chat_id', 'chat_id'),
    )

class DocumentProject(Base):
    """Association table for document-project many-to-many relationship"""
    __tablename__ = "document_projects"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="project_associations")
    project = relationship("Project", back_populates="document_associations")
    
    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint('document_id', 'project_id', name='uq_document_project'),
        Index('idx_document_projects_project_id', 'project_id'),
        Index('idx_document_projects_document_id', 'document_id'),
    )

class Log(Base):
    """Log model for system events and errors"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True)
    log_type = Column(String, nullable=False)  # 'info', 'error', 'process'
    message = Column(Text, nullable=False)
    details = Column(JSON)
    entity_type = Column(String)  # 'document', 'project', 'chat'
    entity_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_logs_entity_type', 'entity_type'),
        Index('idx_logs_log_type', 'log_type'),
    )

class WebSearchCache(Base):
    """Cache for web search results to avoid redundant API calls"""
    __tablename__ = "web_search_cache"
    
    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    results = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_web_search_cache_query', 'query'),
    )