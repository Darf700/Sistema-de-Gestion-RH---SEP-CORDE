from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificacionResponse(BaseModel):
    id: int
    usuario_id: int
    tipo: str
    mensaje: str
    leida: bool
    enlace: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificacionConteo(BaseModel):
    total: int
    no_leidas: int
