from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.notificacion import NotificacionConteo, NotificacionResponse
from ..services.notificacion_service import (
    contar_no_leidas,
    marcar_leida,
    marcar_todas_leidas,
    obtener_notificaciones,
)
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=list[NotificacionResponse])
def listar_notificaciones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return obtener_notificaciones(db, current_user.id)


@router.get("/conteo", response_model=NotificacionConteo)
def conteo_notificaciones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total = len(obtener_notificaciones(db, current_user.id))
    no_leidas = contar_no_leidas(db, current_user.id)
    return NotificacionConteo(total=total, no_leidas=no_leidas)


@router.put("/{notificacion_id}/leer")
def leer_notificacion(
    notificacion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not marcar_leida(db, notificacion_id, current_user.id):
        return {"message": "Notificacion no encontrada"}
    return {"message": "Notificacion marcada como leida"}


@router.put("/leer-todas")
def leer_todas(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = marcar_todas_leidas(db, current_user.id)
    return {"message": f"{count} notificaciones marcadas como leidas"}
