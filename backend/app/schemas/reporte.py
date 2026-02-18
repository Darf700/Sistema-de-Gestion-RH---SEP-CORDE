from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# --- Ausentismo ---
class AusentismoItem(BaseModel):
    empleado_id: int
    nombre_completo: str
    total_ausencias: int
    dias_economicos: int
    permisos_horas: int
    isstep: int
    comisiones: int


class ReporteAusentismoResponse(BaseModel):
    datos: list[AusentismoItem]
    total_registros: int
    periodo: str


# --- Dias Economicos ---
class DiasEconomicosItem(BaseModel):
    empleado_id: int
    nombre_completo: str
    dias_usados: int
    dias_disponibles: int
    solicitudes: int
    fecha_ultima_solicitud: Optional[date] = None


class ReporteDiasEconomicosResponse(BaseModel):
    datos: list[DiasEconomicosItem]
    anio: int
    total_empleados: int


# --- Permisos por Horas ---
class PermisosHorasItem(BaseModel):
    empleado_id: int
    nombre_completo: str
    permisos_q1: int
    permisos_q2: int
    total_permisos: int


class ReportePermisosHorasResponse(BaseModel):
    datos: list[PermisosHorasItem]
    anio: int
    total_empleados: int


# --- Prestaciones ---
class PrestacionesReporteItem(BaseModel):
    id: int
    empleado_id: int
    nombre_completo: str
    tipo: str
    fecha_inicio: date
    fecha_fin: date
    dias_solicitados: Optional[int] = None
    estado: str
    fecha_solicitud: date

    model_config = {"from_attributes": True}


class ReportePrestacionesResponse(BaseModel):
    datos: list[PrestacionesReporteItem]
    total_registros: int
    por_tipo: dict[str, int]
    por_estado: dict[str, int]


# --- Justificantes ---
class JustificantesReporteItem(BaseModel):
    id: int
    empleado_id: int
    nombre_completo: str
    tipo: str
    fecha_inicio: date
    fecha_fin: date
    dias_solicitados: Optional[int] = None
    estado: str
    fecha_generacion: Optional[date] = None

    model_config = {"from_attributes": True}


class ReporteJustificantesResponse(BaseModel):
    datos: list[JustificantesReporteItem]
    total_registros: int
    por_tipo: dict[str, int]
    por_estado: dict[str, int]


# --- Adeudos ---
class AdeudoReporteItem(BaseModel):
    id: int
    empleado_id: int
    nombre_completo: str
    tipo: str
    descripcion: str
    dias_debe: int = 0
    justificante_id: Optional[int] = None
    estado: str
    fecha_marcado: datetime

    model_config = {"from_attributes": True}


class ReporteAdeudosResponse(BaseModel):
    datos: list[AdeudoReporteItem]
    total_registros: int
    total_dias_pendientes: int


# --- Estadisticas Justificantes ---
class EstadisticaTipoItem(BaseModel):
    categoria: str
    valor: str
    conteo: int


class ReporteEstadisticasResponse(BaseModel):
    datos: list[EstadisticaTipoItem]
    total_justificantes: int
    periodo: str
