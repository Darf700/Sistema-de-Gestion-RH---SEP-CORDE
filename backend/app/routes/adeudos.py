from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.adeudo import Adeudo, EstadoAdeudo
from ..models.empleado import Empleado
from ..models.user import User
from ..schemas.adeudo import AdeudoCreate, AdeudoResponse, AdeudoUpdate
from ..services.notificacion_service import crear_notificacion
from ..utils.dependencies import get_current_admin_user, get_current_user
from ..utils.helpers import registrar_auditoria

router = APIRouter()


@router.get("/", response_model=list[AdeudoResponse])
def listar_adeudos(
    empleado_id: int = Query(None),
    estado: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Adeudo)

    if current_user.role.value == "USUARIO":
        query = query.filter(Adeudo.empleado_id == current_user.empleado_id)
    elif empleado_id:
        query = query.filter(Adeudo.empleado_id == empleado_id)

    if estado:
        query = query.filter(Adeudo.estado == estado)

    return query.order_by(Adeudo.fecha_marcado.desc()).all()


@router.post("/", response_model=AdeudoResponse)
def crear_adeudo(
    data: AdeudoCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    empleado = db.query(Empleado).filter(Empleado.id == data.empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    adeudo = Adeudo(
        empleado_id=data.empleado_id,
        tipo=data.tipo,
        descripcion=data.descripcion,
        dias_debe=data.dias_debe,
        justificante_id=data.justificante_id,
        marcado_por_user_id=current_user.id,
    )
    db.add(adeudo)
    db.commit()
    db.refresh(adeudo)

    # Notificar al empleado
    user_empleado = db.query(User).filter(User.empleado_id == data.empleado_id).first()
    if user_empleado:
        crear_notificacion(
            db, user_empleado.id, "adeudo_nuevo",
            f"Tienes un nuevo adeudo: {data.tipo} - {data.descripcion} ({data.dias_debe} dias)",
            enlace=f"/empleado/adeudos",
        )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"marco adeudo a {empleado.nombre_completo}: {data.tipo}",
        "adeudos", adeudo.id,
    )

    return adeudo


@router.put("/{adeudo_id}", response_model=AdeudoResponse)
def actualizar_adeudo(
    adeudo_id: int,
    data: AdeudoUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    adeudo = db.query(Adeudo).filter(Adeudo.id == adeudo_id).first()
    if not adeudo:
        raise HTTPException(status_code=404, detail="Adeudo no encontrado")

    if data.estado:
        adeudo.estado = data.estado
        if data.estado == EstadoAdeudo.RESUELTO:
            adeudo.fecha_resuelto = datetime.utcnow()
    if data.descripcion:
        adeudo.descripcion = data.descripcion
    if data.dias_debe is not None:
        adeudo.dias_debe = data.dias_debe

    db.commit()
    db.refresh(adeudo)

    # Notificar si se resolvio
    if data.estado == EstadoAdeudo.RESUELTO:
        user_empleado = db.query(User).filter(User.empleado_id == adeudo.empleado_id).first()
        if user_empleado:
            crear_notificacion(
                db, user_empleado.id, "adeudo_resuelto",
                f"Tu adeudo '{adeudo.tipo}' ha sido resuelto",
                enlace=f"/empleado/adeudos",
            )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"actualizo adeudo {adeudo.tipo}", "adeudos", adeudo.id,
    )

    return adeudo


@router.delete("/{adeudo_id}")
def eliminar_adeudo(
    adeudo_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    adeudo = db.query(Adeudo).filter(Adeudo.id == adeudo_id).first()
    if not adeudo:
        raise HTTPException(status_code=404, detail="Adeudo no encontrado")

    db.delete(adeudo)
    db.commit()

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"elimino adeudo {adeudo.tipo}", "adeudos", adeudo_id,
    )

    return {"message": "Adeudo eliminado"}
