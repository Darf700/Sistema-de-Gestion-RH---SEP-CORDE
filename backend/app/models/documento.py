import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text

from ..database import Base


class EstadoDocumento(str, enum.Enum):
    PENDIENTE = "Pendiente"
    EN_PROCESO = "En Proceso"
    LISTO = "Listo"
    ENTREGADO = "Entregado"


class OrigenSolicitud(str, enum.Enum):
    EMPLEADO = "Empleado"  # Empleado solicita a RH
    RH = "RH"             # RH solicita al empleado


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    tipo = Column(String, nullable=False)  # Constancia laboral, CURP, etc.
    descripcion = Column(Text, nullable=True)

    origen = Column(SQLEnum(OrigenSolicitud), nullable=False)
    estado = Column(SQLEnum(EstadoDocumento), default=EstadoDocumento.PENDIENTE)

    archivo_path = Column(String, nullable=True)
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    fecha_entrega = Column(DateTime, nullable=True)

    solicitado_por_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
