import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class UserRole(str, enum.Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=True)

    active = Column(Boolean, default=True)
    password_changed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    empleado = relationship("Empleado", backref="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
