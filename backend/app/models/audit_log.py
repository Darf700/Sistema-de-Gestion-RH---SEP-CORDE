from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    accion = Column(String, nullable=False)
    tabla_afectada = Column(String, nullable=True)
    registro_id = Column(Integer, nullable=True)
    datos_anteriores = Column(Text, nullable=True)  # JSON
    datos_nuevos = Column(Text, nullable=True)       # JSON
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
