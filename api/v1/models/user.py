"""
User model for the QA RAG Bot API using SQLAlchemy
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Index
from sqlalchemy.sql import func
from api.v1.config.dbconnection import Base


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model"""
    __tablename__ = "users"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)

    # User fields
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        info={"description": "User email address"}
    )
    
    first_name = Column(
        String(64),
        nullable=False,
        info={"description": "User first name (2-64 chars)"}
    )
    
    last_name = Column(
        String(64),
        nullable=False,
        info={"description": "User last name (2-64 chars)"}
    )
    
    password = Column(
        String(255),
        nullable=False,
        info={"description": "Hashed password (min 8 chars)"}
    )
    
    role = Column(
        String(20),
        default=UserRole.USER.value,
        nullable=False,
        info={"description": "User role (user or admin)"}
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        info={"description": "Whether the user account is active"}
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        info={"description": "Account creation timestamp"}
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        info={"description": "Last update timestamp"}
    )

    # Indexes
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_role', 'role'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self, include_password=False):
        """
        Convert user to dictionary representation
        
        Args:
            include_password (bool): Whether to include password hash in output
        
        Returns:
            dict: User data as dictionary
        """
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_password:
            data['password'] = self.password
            
        return data
