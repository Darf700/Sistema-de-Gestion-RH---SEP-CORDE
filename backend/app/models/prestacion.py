import enum
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text

from ..database import Base


class TipoPrestacion(str, enum.Enum):
    LICENCIA_MEDICA = "Licencia Medica"
    CUIDADOS_MATERNOS = "Cuidados Maternos/Paternos"
    CUIDADOS_MEDICOS_FAMILIARES = "Cuidados Medicos Familiares"
    FALLECIMIENTO_FAMILIAR = "Fallecimiento de Familiar"
    MEDIA_HORA_TOLERANCIA = "Media Hora de Tolerancia"
    LICENCIA_NUPCIAS = "Licencia por Nupcias"
    LICENCIA_PATERNIDAD = "Licencia por Paternidad"


class EstadoPrestacion(str, enum.Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"
    RECHAZADA = "Rechazada"


class Prestacion(Base):
    __tablename__ = "prestaciones"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    tipo = Column(SQLEnum(TipoPrestacion), nullable=False)

    fecha_solicitud = Column(Date, default=datetime.utcnow)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    dias_solicitados = Column(Integer, nullable=True)

    motivo = Column(Text, nullable=True)
    documentos_adjuntos = Column(String, nullable=True)  # JSON: lista de paths

    estado = Column(SQLEnum(EstadoPrestacion), default=EstadoPrestacion.PENDIENTE)
    aprobado_por_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    motivo_rechazo = Column(Text, nullable=True)

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
