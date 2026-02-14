from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.contador import Contador
from ..models.empleado import Empleado
from ..models.user import User
from ..schemas.empleado import ContadorResponse, EmpleadoCreate, EmpleadoResponse, EmpleadoUpdate
from ..utils.dependencies import get_current_admin_user, get_current_user
from ..utils.helpers import registrar_auditoria

router = APIRouter()


@router.get("/", response_model=list[EmpleadoResponse])
def listar_empleados(
    activo: bool = Query(True),
    tipo: str = Query(None),
    buscar: str = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Empleado).filter(Empleado.activo == activo)
    if tipo:
        query = query.filter(Empleado.tipo == tipo)
    if buscar:
        query = query.filter(Empleado.nombre_completo.ilike(f"%{buscar}%"))
    return query.order_by(Empleado.nombre_completo).all()


@router.get("/{empleado_id}", response_model=EmpleadoResponse)
def obtener_empleado(
    empleado_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Usuarios normales solo pueden ver su propio perfil
    if current_user.role.value == "USUARIO" and current_user.empleado_id != empleado_id:
        raise HTTPException(status_code=403, detail="Solo puedes ver tu propio perfil")

    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.post("/", response_model=EmpleadoResponse)
def crear_empleado(
    data: EmpleadoCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    empleado = Empleado(**data.model_dump())
    db.add(empleado)
    db.commit()
    db.refresh(empleado)

    # Crear contador para el anio actual
    contador = Contador(empleado_id=empleado.id, anio=date.today().year)
    db.add(contador)
    db.commit()

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"creo empleado {empleado.nombre_completo}", "empleados", empleado.id,
    )
    return empleado


@router.put("/{empleado_id}", response_model=EmpleadoResponse)
def actualizar_empleado(
    empleado_id: int,
    data: EmpleadoUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(empleado, key, value)
    db.commit()
    db.refresh(empleado)

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"actualizo empleado {empleado.nombre_completo}",
        "empleados", empleado.id, datos_nuevos=update_data,
    )
    return empleado


@router.delete("/{empleado_id}")
def eliminar_empleado(
    empleado_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    empleado.activo = False
    db.commit()

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"desactivo empleado {empleado.nombre_completo}", "empleados", empleado.id,
    )
    return {"message": f"Empleado {empleado.nombre_completo} desactivado"}


@router.get("/{empleado_id}/contadores", response_model=ContadorResponse)
def obtener_contadores(
    empleado_id: int,
    anio: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value == "USUARIO" and current_user.empleado_id != empleado_id:
        raise HTTPException(status_code=403, detail="Solo puedes ver tus propios contadores")

    if anio is None:
        anio = date.today().year

    contador = db.query(Contador).filter(
        Contador.empleado_id == empleado_id, Contador.anio == anio
    ).first()

    if not contador:
        # Crear contador si no existe
        contador = Contador(empleado_id=empleado_id, anio=anio)
        db.add(contador)
        db.commit()
        db.refresh(contador)

    return contador
