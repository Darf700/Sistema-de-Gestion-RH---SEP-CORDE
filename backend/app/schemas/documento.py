from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.documento import EstadoDocumento, OrigenSolicitud


class DocumentoCreate(BaseModel):
    empleado_id: Optional[int] = None  # None = el propio empleado
    tipo: str
    descripcion: Optional[str] = None


class DocumentoUpdateEstado(BaseModel):
    estado: EstadoDocumento


class DocumentoResponse(BaseModel):
    id: int
    empleado_id: int
    tipo: str
    descripcion: Optional[str] = None
    origen: OrigenSolicitud
    estado: EstadoDocumento
    archivo_path: Optional[str] = None
    fecha_solicitud: datetime
    fecha_entrega: Optional[datetime] = None
    solicitado_por_user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
