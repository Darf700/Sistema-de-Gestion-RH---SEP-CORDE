import enum

from sqlalchemy import Column, Date, Enum as SQLEnum, Integer, String

from ..database import Base


class TipoDia(str, enum.Enum):
    FESTIVO = "Festivo"
    VACACION = "Vacacion"
    LABORAL = "Laboral"


class CalendarioLaboral(Base):
    __tablename__ = "calendario_laboral"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    tipo = Column(SQLEnum(TipoDia), nullable=False)
    descripcion = Column(String, nullable=True)
    anio = Column(Integer, nullable=False)
