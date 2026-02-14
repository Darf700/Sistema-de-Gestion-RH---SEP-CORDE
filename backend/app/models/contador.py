from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String

from ..database import Base


class Contador(Base):
    __tablename__ = "contadores"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    anio = Column(Integer, nullable=False)

    # Dias economicos
    dias_economicos_usados = Column(Integer, default=0)
    solicitudes_economicos = Column(Integer, default=0)
    fecha_ultima_solicitud_economico = Column(Date, nullable=True)

    # Permisos por horas (se trackea por quincena en la logica, aqui el acumulado)
    permisos_horas_q1 = Column(Integer, default=0)  # Quincena actual
    permisos_horas_q2 = Column(Integer, default=0)

    # Prestaciones
    cuidados_maternos_usados = Column(Integer, default=0)
    cuidados_medicos_usados = Column(Integer, default=0)

    # JSON para otras prestaciones flexibles
    otras_prestaciones = Column(String, default="{}")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
