from datetime import date
from typing import Optional

from pydantic import BaseModel

from ..models.empleado import TipoEmpleado, TipoNombramiento


class EmpleadoCreate(BaseModel):
    nombre_completo: str
    claves_presupuestales: str
    horario: str
    adscripcion: str
    numero_asistencia: str
    tipo: TipoEmpleado
    nombramiento: TipoNombramiento = TipoNombramiento.BASE
    fecha_ingreso: date
    email: Optional[str] = None
    telefono: Optional[str] = None


class EmpleadoUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    claves_presupuestales: Optional[str] = None
    horario: Optional[str] = None
    adscripcion: Optional[str] = None
    numero_asistencia: Optional[str] = None
    tipo: Optional[TipoEmpleado] = None
    nombramiento: Optional[TipoNombramiento] = None
    fecha_ingreso: Optional[date] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class EmpleadoResponse(BaseModel):
    id: int
    nombre_completo: str
    claves_presupuestales: str
    horario: str
    adscripcion: str
    numero_asistencia: str
    tipo: TipoEmpleado
    nombramiento: TipoNombramiento
    fecha_ingreso: date
    activo: bool
    email: Optional[str] = None
    telefono: Optional[str] = None
    antiguedad_meses: int
    cumple_antiguedad_minima: bool

    model_config = {"from_attributes": True}


class ContadorResponse(BaseModel):
    anio: int
    dias_economicos_usados: int
    solicitudes_economicos: int
    fecha_ultima_solicitud_economico: Optional[date] = None
    permisos_horas_q1: int
    permisos_horas_q2: int
    cuidados_maternos_usados: int
    cuidados_medicos_usados: int

    model_config = {"from_attributes": True}
