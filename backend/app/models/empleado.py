import enum
from datetime import date

from sqlalchemy import Boolean, Column, Date, Enum as SQLEnum, Integer, String

from ..database import Base


class TipoEmpleado(str, enum.Enum):
    DOCENTE = "Docente"
    APOYO = "Apoyo y Asistencia"


class TipoNombramiento(str, enum.Enum):
    BASE = "Base"
    INTERINO = "Interino"
    LIMITADO = "Limitado"
    GRAVIDEZ = "Gravidez"
    PREJUBILATORIO = "Prejubilatorio"
    HONORARIOS = "Honorarios"


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False, index=True)
    claves_presupuestales = Column(String, nullable=False)
    horario = Column(String, nullable=False)
    adscripcion = Column(String, nullable=False)
    numero_asistencia = Column(String, nullable=False)
    tipo = Column(SQLEnum(TipoEmpleado), nullable=False)
    nombramiento = Column(SQLEnum(TipoNombramiento), default=TipoNombramiento.BASE)

    fecha_ingreso = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)

    # Contacto
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)

    # Beneficiarios / Emergencia (JSON string)
    beneficiarios = Column(String, nullable=True)
    contactos_emergencia = Column(String, nullable=True)

    def __repr__(self):
        return f"<Empleado {self.nombre_completo}>"

    @property
    def antiguedad_meses(self) -> int:
        hoy = date.today()
        meses = (hoy.year - self.fecha_ingreso.year) * 12
        meses += hoy.month - self.fecha_ingreso.month
        if hoy.day < self.fecha_ingreso.day:
            meses -= 1
        return meses

    @property
    def cumple_antiguedad_minima(self) -> bool:
        """6 meses + 1 dia de antiguedad."""
        return self.antiguedad_meses >= 6
