from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from ..database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tipo = Column(String, nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False)
    enlace = Column(String, nullable=True)  # URL relativa para navegar al recurso
    created_at = Column(DateTime, default=datetime.utcnow)
