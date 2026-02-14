import enum
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Time

from ..database import Base


class TipoJustificante(str, enum.Enum):
    DIA_ECONOMICO = "Dia Economico"
    PERMISO_HORAS = "Permiso por Horas"
    ISSTEP = "ISSTEP"
    COMISION_DIA = "Comision Todo el Dia"
    COMISION_ENTRADA = "Comision Entrada"
    COMISION_SALIDA = "Comision Salida"


class EstadoJustificante(str, enum.Enum):
    GENERADO = "Generado"
    ENTREGADO = "Entregado"
    EXTEMPORANEO = "Extemporaneo"


class Justificante(Base):
    __tablename__ = "justificantes"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    tipo = Column(SQLEnum(TipoJustificante), nullable=False)

    fecha_generacion = Column(Date, default=datetime.utcnow)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    dias_solicitados = Column(Integer, nullable=True)

    motivo = Column(String, nullable=True)
    lugar = Column(String, nullable=True)  # Para comisiones

    hora_inicio = Column(Time, nullable=True)  # Para permisos por horas
    hora_fin = Column(Time, nullable=True)

    pdf_path = Column(String, nullable=True)
    estado = Column(SQLEnum(EstadoJustificante), default=EstadoJustificante.GENERADO)

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
