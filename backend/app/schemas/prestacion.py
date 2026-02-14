from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from ..models.prestacion import EstadoPrestacion, TipoPrestacion


class PrestacionCreate(BaseModel):
    tipo: TipoPrestacion
    fecha_inicio: date
    fecha_fin: date
    dias_solicitados: Optional[int] = None
    motivo: Optional[str] = None


class PrestacionUpdate(BaseModel):
    estado: Optional[EstadoPrestacion] = None
    motivo_rechazo: Optional[str] = None


class PrestacionResponse(BaseModel):
    id: int
    empleado_id: int
    tipo: TipoPrestacion
    fecha_solicitud: date
    fecha_inicio: date
    fecha_fin: date
    dias_solicitados: Optional[int] = None
    motivo: Optional[str] = None
    documentos_adjuntos: Optional[str] = None
    estado: EstadoPrestacion
    aprobado_por_user_id: Optional[int] = None
    motivo_rechazo: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PrestacionValidacionResponse(BaseModel):
    valido: bool
    errores: list[str] = []
    advertencias: list[str] = []
    documentos_requeridos: list[str] = []
    dias_maximos: Optional[int] = None


class CatalogoPrestacion(BaseModel):
    tipo: TipoPrestacion
    nombre: str
    descripcion: str
    dias_maximos: Optional[int] = None
    documentos_requeridos: list[str]
    requisitos: list[str]
