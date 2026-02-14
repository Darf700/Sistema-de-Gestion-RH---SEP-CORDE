import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.contador import Contador
from ..models.empleado import Empleado, TipoEmpleado
from ..models.prestacion import EstadoPrestacion, Prestacion, TipoPrestacion
from ..models.user import User
from ..schemas.prestacion import (
    CatalogoPrestacion,
    PrestacionCreate,
    PrestacionResponse,
    PrestacionUpdate,
    PrestacionValidacionResponse,
)
from ..services.calendario_service import calendario_service
from ..services.notificacion_service import crear_notificacion
from ..utils.dependencies import get_current_admin_user, get_current_user
from ..utils.helpers import registrar_auditoria
from ..validators.prestacion_validator import (
    CATALOGO_PRESTACIONES,
    validar_prestacion,
)

router = APIRouter()


@router.get("/catalogo", response_model=list[CatalogoPrestacion])
def obtener_catalogo():
    catalogo = []
    for tipo, info in CATALOGO_PRESTACIONES.items():
        catalogo.append(
            CatalogoPrestacion(
                tipo=tipo,
                nombre=info["nombre"],
                descripcion=info["descripcion"],
                dias_maximos=info["dias_maximos"],
                documentos_requeridos=info["documentos_requeridos"],
                requisitos=info["requisitos"],
            )
        )
    return catalogo


@router.get("/", response_model=list[PrestacionResponse])
def listar_prestaciones(
    empleado_id: int = Query(None),
    tipo: str = Query(None),
    estado: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Prestacion)

    if current_user.role.value == "USUARIO":
        query = query.filter(Prestacion.empleado_id == current_user.empleado_id)
    elif empleado_id:
        query = query.filter(Prestacion.empleado_id == empleado_id)

    if tipo:
        query = query.filter(Prestacion.tipo == tipo)
    if estado:
        query = query.filter(Prestacion.estado == estado)

    return query.order_by(Prestacion.created_at.desc()).all()


@router.post("/validar", response_model=PrestacionValidacionResponse)
def validar_prestacion_endpoint(
    data: PrestacionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    empleado_id = current_user.empleado_id
    if not empleado_id:
        raise HTTPException(status_code=400, detail="Usuario no tiene empleado asociado")

    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    return validar_prestacion(
        db, empleado, data.tipo, data.fecha_inicio, data.fecha_fin, data.dias_solicitados
    )


@router.post("/", response_model=PrestacionResponse)
def crear_prestacion(
    data: PrestacionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    empleado_id = current_user.empleado_id
    if not empleado_id:
        raise HTTPException(status_code=400, detail="Usuario no tiene empleado asociado")

    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Validar
    validacion = validar_prestacion(
        db, empleado, data.tipo, data.fecha_inicio, data.fecha_fin, data.dias_solicitados
    )
    if not validacion.valido:
        raise HTTPException(status_code=400, detail="; ".join(validacion.errores))

    dias_lab = calendario_service.calcular_dias_laborales(data.fecha_inicio, data.fecha_fin)

    prestacion = Prestacion(
        empleado_id=empleado_id,
        tipo=data.tipo,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        dias_solicitados=dias_lab,
        motivo=data.motivo,
        created_by_user_id=current_user.id,
    )
    db.add(prestacion)
    db.commit()
    db.refresh(prestacion)

    # Notificar a admins
    admins = db.query(User).filter(User.role.in_(["ROOT", "ADMIN"]), User.active == True).all()
    for admin in admins:
        crear_notificacion(
            db, admin.id, "nueva_prestacion",
            f"{empleado.nombre_completo} solicito {data.tipo.value}",
            enlace=f"/rh/prestaciones/{prestacion.id}",
        )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"solicito prestacion {data.tipo.value}", "prestaciones", prestacion.id,
    )

    return prestacion


@router.put("/{prestacion_id}/aprobar", response_model=PrestacionResponse)
def aprobar_prestacion(
    prestacion_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    prestacion = db.query(Prestacion).filter(Prestacion.id == prestacion_id).first()
    if not prestacion:
        raise HTTPException(status_code=404, detail="Prestacion no encontrada")

    if prestacion.estado != EstadoPrestacion.PENDIENTE:
        raise HTTPException(status_code=400, detail="La prestacion ya fue procesada")

    prestacion.estado = EstadoPrestacion.APROBADA
    prestacion.aprobado_por_user_id = current_user.id
    prestacion.updated_at = datetime.utcnow()

    # Actualizar contadores
    _actualizar_contadores_prestacion(db, prestacion)

    db.commit()
    db.refresh(prestacion)

    # Notificar al empleado
    user_empleado = db.query(User).filter(User.empleado_id == prestacion.empleado_id).first()
    if user_empleado:
        crear_notificacion(
            db, user_empleado.id, "prestacion_aprobada",
            f"Tu solicitud de {prestacion.tipo.value} fue aprobada",
            enlace=f"/empleado/prestaciones/{prestacion.id}",
        )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"aprobo prestacion {prestacion.tipo.value}", "prestaciones", prestacion.id,
    )

    return prestacion


@router.put("/{prestacion_id}/rechazar", response_model=PrestacionResponse)
def rechazar_prestacion(
    prestacion_id: int,
    data: PrestacionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    prestacion = db.query(Prestacion).filter(Prestacion.id == prestacion_id).first()
    if not prestacion:
        raise HTTPException(status_code=404, detail="Prestacion no encontrada")

    if prestacion.estado != EstadoPrestacion.PENDIENTE:
        raise HTTPException(status_code=400, detail="La prestacion ya fue procesada")

    prestacion.estado = EstadoPrestacion.RECHAZADA
    prestacion.motivo_rechazo = data.motivo_rechazo
    prestacion.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prestacion)

    # Notificar al empleado
    user_empleado = db.query(User).filter(User.empleado_id == prestacion.empleado_id).first()
    if user_empleado:
        motivo = f" Motivo: {data.motivo_rechazo}" if data.motivo_rechazo else ""
        crear_notificacion(
            db, user_empleado.id, "prestacion_rechazada",
            f"Tu solicitud de {prestacion.tipo.value} fue rechazada.{motivo}",
            enlace=f"/empleado/prestaciones/{prestacion.id}",
        )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"rechazo prestacion {prestacion.tipo.value}", "prestaciones", prestacion.id,
    )

    return prestacion


@router.post("/{prestacion_id}/documentos")
async def subir_documento_prestacion(
    prestacion_id: int,
    archivo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prestacion = db.query(Prestacion).filter(Prestacion.id == prestacion_id).first()
    if not prestacion:
        raise HTTPException(status_code=404, detail="Prestacion no encontrada")

    if (
        current_user.role.value == "USUARIO"
        and prestacion.empleado_id != current_user.empleado_id
    ):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta prestacion")

    # Guardar archivo
    upload_dir = os.path.join(
        settings.DOCUMENTOS_DIR, str(prestacion.empleado_id), "prestaciones"
    )
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{prestacion_id}_{archivo.filename}")

    with open(file_path, "wb") as f:
        content = await archivo.read()
        f.write(content)

    # Actualizar lista de documentos
    docs = json.loads(prestacion.documentos_adjuntos or "[]")
    docs.append(file_path)
    prestacion.documentos_adjuntos = json.dumps(docs)
    db.commit()

    return {"message": "Documento subido exitosamente", "path": file_path}


@router.get("/{prestacion_id}", response_model=PrestacionResponse)
def obtener_prestacion(
    prestacion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prestacion = db.query(Prestacion).filter(Prestacion.id == prestacion_id).first()
    if not prestacion:
        raise HTTPException(status_code=404, detail="Prestacion no encontrada")

    if (
        current_user.role.value == "USUARIO"
        and prestacion.empleado_id != current_user.empleado_id
    ):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta prestacion")

    return prestacion


def _actualizar_contadores_prestacion(db: Session, prestacion: Prestacion):
    """Actualiza contadores cuando una prestacion es aprobada."""
    anio = prestacion.fecha_inicio.year
    contador = db.query(Contador).filter(
        Contador.empleado_id == prestacion.empleado_id, Contador.anio == anio
    ).first()
    if not contador:
        contador = Contador(empleado_id=prestacion.empleado_id, anio=anio)
        db.add(contador)
        db.flush()

    dias = prestacion.dias_solicitados or 0

    if prestacion.tipo == TipoPrestacion.CUIDADOS_MATERNOS:
        contador.cuidados_maternos_usados += dias
    elif prestacion.tipo == TipoPrestacion.CUIDADOS_MEDICOS_FAMILIARES:
        contador.cuidados_medicos_usados += dias
