from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel

from ..models.justificante import EstadoJustificante, TipoJustificante


class JustificanteCreate(BaseModel):
    tipo: TipoJustificante
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    motivo: Optional[str] = None
    lugar: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None


class JustificanteResponse(BaseModel):
    id: int
    empleado_id: int
    tipo: TipoJustificante
    fecha_generacion: date
    fecha_inicio: date
    fecha_fin: date
    dias_solicitados: Optional[int] = None
    motivo: Optional[str] = None
    lugar: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    pdf_path: Optional[str] = None
    estado: EstadoJustificante
    created_at: datetime

    model_config = {"from_attributes": True}


class ValidacionResponse(BaseModel):
    valido: bool
    errores: list[str] = []
    advertencias: list[str] = []
    fecha_inicio_calculada: Optional[date] = None
    fecha_fin_calculada: Optional[date] = None
