from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.adeudo import EstadoAdeudo


class AdeudoCreate(BaseModel):
    empleado_id: int
    tipo: str
    descripcion: str
    dias_debe: int = 0
    justificante_id: Optional[int] = None


class AdeudoUpdate(BaseModel):
    estado: Optional[EstadoAdeudo] = None
    descripcion: Optional[str] = None
    dias_debe: Optional[int] = None


class AdeudoResponse(BaseModel):
    id: int
    empleado_id: int
    tipo: str
    descripcion: str
    dias_debe: int = 0
    justificante_id: Optional[int] = None
    estado: EstadoAdeudo
    marcado_por_user_id: int
    fecha_marcado: datetime
    fecha_resuelto: Optional[datetime] = None

    model_config = {"from_attributes": True}
