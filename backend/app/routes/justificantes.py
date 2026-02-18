from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.contador import Contador
from ..models.empleado import Empleado
from ..models.justificante import Justificante, TipoJustificante
from ..models.user import User
from ..schemas.justificante import JustificanteCreate, JustificanteResponse, ValidacionResponse
from ..services.calendario_service import calendario_service
from ..services.pdf_service import generar_pdf_justificante, guardar_pdf
from ..utils.dependencies import get_current_admin_user, get_current_user
from ..utils.helpers import registrar_auditoria
from ..validators.dia_economico_validator import validar_dia_economico
from ..validators.permiso_horas_validator import validar_permiso_horas

router = APIRouter()


@router.get("/", response_model=list[JustificanteResponse])
def listar_justificantes(
    empleado_id: int = Query(None),
    tipo: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Justificante)

    if current_user.role.value == "USUARIO":
        query = query.filter(Justificante.empleado_id == current_user.empleado_id)
    elif empleado_id:
        query = query.filter(Justificante.empleado_id == empleado_id)

    if tipo:
        query = query.filter(Justificante.tipo == tipo)

    return query.order_by(Justificante.created_at.desc()).all()


@router.post("/validar", response_model=ValidacionResponse)
def validar_justificante(
    data: JustificanteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    empleado_id = current_user.empleado_id
    if not empleado_id:
        raise HTTPException(status_code=400, detail="Usuario no tiene empleado asociado")

    if data.tipo == TipoJustificante.DIA_ECONOMICO:
        return validar_dia_economico(db, empleado_id, data.fecha_inicio)
    elif data.tipo == TipoJustificante.PERMISO_HORAS:
        return validar_permiso_horas(db, empleado_id, data.fecha_inicio)
    else:
        return ValidacionResponse(
            valido=True,
            fecha_inicio_calculada=data.fecha_inicio,
            fecha_fin_calculada=data.fecha_fin or data.fecha_inicio,
        )


@router.post("/", response_model=JustificanteResponse)
def crear_justificante(
    data: JustificanteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    empleado_id = current_user.empleado_id
    if not empleado_id:
        raise HTTPException(status_code=400, detail="Usuario no tiene empleado asociado")

    # Validar primero
    if data.tipo == TipoJustificante.DIA_ECONOMICO:
        validacion = validar_dia_economico(db, empleado_id, data.fecha_inicio)
        if not validacion.valido:
            raise HTTPException(status_code=400, detail="; ".join(validacion.errores))
        fecha_fin = validacion.fecha_fin_calculada
        dias = 3
    elif data.tipo == TipoJustificante.PERMISO_HORAS:
        validacion = validar_permiso_horas(db, empleado_id, data.fecha_inicio)
        if not validacion.valido:
            raise HTTPException(status_code=400, detail="; ".join(validacion.errores))
        fecha_fin = data.fecha_inicio
        dias = None
    else:
        fecha_fin = data.fecha_fin or data.fecha_inicio
        dias = calendario_service.calcular_dias_laborales(data.fecha_inicio, fecha_fin) if data.fecha_fin else None

    justificante = Justificante(
        empleado_id=empleado_id,
        tipo=data.tipo,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=fecha_fin,
        dias_solicitados=dias,
        motivo=data.motivo,
        lugar=data.lugar,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        created_by_user_id=current_user.id,
    )
    db.add(justificante)
    db.flush()

    # Actualizar contadores
    if data.tipo == TipoJustificante.DIA_ECONOMICO:
        anio = data.fecha_inicio.year
        contador = db.query(Contador).filter(
            Contador.empleado_id == empleado_id, Contador.anio == anio
        ).first()
        if not contador:
            contador = Contador(empleado_id=empleado_id, anio=anio)
            db.add(contador)
            db.flush()
        contador.solicitudes_economicos += 1
        contador.dias_economicos_usados += 3
        contador.fecha_ultima_solicitud_economico = data.fecha_inicio

    db.commit()
    db.refresh(justificante)

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"genero justificante {data.tipo.value}", "justificantes", justificante.id,
    )

    return justificante


@router.get("/tipos")
def listar_tipos():
    return [{"value": t.value, "label": t.value} for t in TipoJustificante]


@router.get("/{justificante_id}", response_model=JustificanteResponse)
def obtener_justificante(
    justificante_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    justificante = db.query(Justificante).filter(Justificante.id == justificante_id).first()
    if not justificante:
        raise HTTPException(status_code=404, detail="Justificante no encontrado")

    if (
        current_user.role.value == "USUARIO"
        and justificante.empleado_id != current_user.empleado_id
    ):
        raise HTTPException(status_code=403, detail="No tienes acceso a este justificante")

    return justificante


@router.get("/{justificante_id}/pdf")
def descargar_pdf_justificante(
    justificante_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    justificante = db.query(Justificante).filter(Justificante.id == justificante_id).first()
    if not justificante:
        raise HTTPException(status_code=404, detail="Justificante no encontrado")

    if (
        current_user.role.value == "USUARIO"
        and justificante.empleado_id != current_user.empleado_id
    ):
        raise HTTPException(status_code=403, detail="No tienes acceso a este justificante")

    empleado = db.query(Empleado).filter(Empleado.id == justificante.empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    pdf_buffer = generar_pdf_justificante(justificante, empleado)

    # Guardar en disco y actualizar registro
    filename = f"justificante_{justificante.id}.pdf"
    saved_path = guardar_pdf(pdf_buffer, "justificantes", filename)
    justificante.pdf_path = saved_path
    db.commit()

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"descargo PDF justificante #{justificante.id}", "justificantes", justificante.id,
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
