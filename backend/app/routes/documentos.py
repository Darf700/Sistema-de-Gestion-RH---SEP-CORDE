import os
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.documento import Documento, EstadoDocumento, OrigenSolicitud
from ..models.empleado import Empleado
from ..models.user import User
from ..schemas.documento import DocumentoCreate, DocumentoResponse, DocumentoUpdateEstado
from ..services.notificacion_service import crear_notificacion
from ..utils.dependencies import get_current_admin_user, get_current_user
from ..utils.helpers import registrar_auditoria

router = APIRouter()


@router.get("/", response_model=list[DocumentoResponse])
def listar_documentos(
    empleado_id: int = Query(None),
    origen: str = Query(None),
    estado: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Documento)

    if current_user.role.value == "USUARIO":
        query = query.filter(Documento.empleado_id == current_user.empleado_id)
    elif empleado_id:
        query = query.filter(Documento.empleado_id == empleado_id)

    if origen:
        query = query.filter(Documento.origen == origen)
    if estado:
        query = query.filter(Documento.estado == estado)

    return query.order_by(Documento.created_at.desc()).all()


@router.post("/solicitar-a-rh", response_model=DocumentoResponse)
def solicitar_documento_a_rh(
    data: DocumentoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Empleado solicita un documento a RH (constancia laboral, etc.)."""
    if not current_user.empleado_id:
        raise HTTPException(status_code=400, detail="Usuario no tiene empleado asociado")

    documento = Documento(
        empleado_id=current_user.empleado_id,
        tipo=data.tipo,
        descripcion=data.descripcion,
        origen=OrigenSolicitud.EMPLEADO,
        solicitado_por_user_id=current_user.id,
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)

    # Notificar a admins
    empleado = db.query(Empleado).filter(Empleado.id == current_user.empleado_id).first()
    admins = db.query(User).filter(User.role.in_(["ROOT", "ADMIN"]), User.active == True).all()
    for admin in admins:
        crear_notificacion(
            db, admin.id, "solicitud_documento",
            f"{empleado.nombre_completo} solicito: {data.tipo}",
            enlace=f"/rh/documentos/{documento.id}",
        )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"solicito documento: {data.tipo}", "documentos", documento.id,
    )

    return documento


@router.post("/solicitar-a-empleado", response_model=DocumentoResponse)
def solicitar_documento_a_empleado(
    data: DocumentoCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """RH solicita un documento al empleado (CURP actualizado, etc.)."""
    if not data.empleado_id:
        raise HTTPException(status_code=400, detail="Debe especificar empleado_id")

    empleado = db.query(Empleado).filter(Empleado.id == data.empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    documento = Documento(
        empleado_id=data.empleado_id,
        tipo=data.tipo,
        descripcion=data.descripcion,
        origen=OrigenSolicitud.RH,
        solicitado_por_user_id=current_user.id,
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)

    # Notificar al empleado
    user_empleado = db.query(User).filter(User.empleado_id == data.empleado_id).first()
    if user_empleado:
        crear_notificacion(
            db, user_empleado.id, "documento_solicitado",
            f"RH te solicita: {data.tipo}",
            enlace=f"/empleado/documentos/{documento.id}",
        )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"solicito a empleado {empleado.nombre_completo}: {data.tipo}",
        "documentos", documento.id,
    )

    return documento


@router.put("/{documento_id}/estado", response_model=DocumentoResponse)
def actualizar_estado_documento(
    documento_id: int,
    data: DocumentoUpdateEstado,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    documento.estado = data.estado
    if data.estado == EstadoDocumento.ENTREGADO:
        documento.fecha_entrega = datetime.utcnow()

    db.commit()
    db.refresh(documento)

    # Notificar si esta listo
    if data.estado == EstadoDocumento.LISTO:
        user_empleado = db.query(User).filter(User.empleado_id == documento.empleado_id).first()
        if user_empleado:
            crear_notificacion(
                db, user_empleado.id, "documento_listo",
                f"Tu documento '{documento.tipo}' esta listo",
                enlace=f"/empleado/documentos/{documento.id}",
            )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"cambio estado documento a {data.estado.value}", "documentos", documento.id,
    )

    return documento


@router.post("/{documento_id}/upload")
async def subir_archivo_documento(
    documento_id: int,
    archivo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # Empleado solo puede subir a sus propios documentos
    if (
        current_user.role.value == "USUARIO"
        and documento.empleado_id != current_user.empleado_id
    ):
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    upload_dir = os.path.join(
        settings.DOCUMENTOS_DIR, str(documento.empleado_id), "solicitudes"
    )
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{documento_id}_{archivo.filename}")

    with open(file_path, "wb") as f:
        content = await archivo.read()
        f.write(content)

    documento.archivo_path = file_path
    db.commit()

    # Notificar a RH si empleado subio archivo
    if documento.origen == OrigenSolicitud.RH and current_user.role.value == "USUARIO":
        empleado = db.query(Empleado).filter(Empleado.id == documento.empleado_id).first()
        admins = db.query(User).filter(
            User.role.in_(["ROOT", "ADMIN"]), User.active == True
        ).all()
        for admin in admins:
            crear_notificacion(
                db, admin.id, "documento_subido",
                f"{empleado.nombre_completo} subio: {documento.tipo}",
                enlace=f"/rh/documentos/{documento.id}",
            )

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"subio archivo para documento {documento.tipo}", "documentos", documento.id,
    )

    return {"message": "Archivo subido exitosamente", "path": file_path}


@router.get("/{documento_id}", response_model=DocumentoResponse)
def obtener_documento(
    documento_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if (
        current_user.role.value == "USUARIO"
        and documento.empleado_id != current_user.empleado_id
    ):
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    return documento
