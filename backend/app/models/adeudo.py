import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text

from ..database import Base


class EstadoAdeudo(str, enum.Enum):
    PENDIENTE = "Pendiente"
    RESUELTO = "Resuelto"


class TipoAdeudo(str, enum.Enum):
    DIAS_PENDIENTES = "Dias pendientes"
    JUSTIFICANTE_NO_ENTREGADO = "Justificante no entregado"
    DOCUMENTO_PENDIENTE = "Documento pendiente"


class Adeudo(Base):
    __tablename__ = "adeudos"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    tipo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    dias_debe = Column(Integer, default=0)
    justificante_id = Column(Integer, ForeignKey("justificantes.id"), nullable=True)

    estado = Column(SQLEnum(EstadoAdeudo), default=EstadoAdeudo.PENDIENTE)
    marcado_por_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    fecha_marcado = Column(DateTime, default=datetime.utcnow)
    fecha_resuelto = Column(DateTime, nullable=True)
