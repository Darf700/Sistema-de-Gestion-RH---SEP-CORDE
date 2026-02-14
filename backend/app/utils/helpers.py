import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from ..models.audit_log import AuditLog


def registrar_auditoria(
    db: Session,
    user_id: int,
    username: str,
    accion: str,
    tabla_afectada: str = None,
    registro_id: int = None,
    datos_anteriores: dict = None,
    datos_nuevos: dict = None,
    ip_address: str = None,
):
    log = AuditLog(
        user_id=user_id,
        username=username,
        accion=accion,
        tabla_afectada=tabla_afectada,
        registro_id=registro_id,
        datos_anteriores=json.dumps(datos_anteriores, default=str) if datos_anteriores else None,
        datos_nuevos=json.dumps(datos_nuevos, default=str) if datos_nuevos else None,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()


def obtener_quincena(fecha: date = None) -> int:
    """Retorna 1 o 2 segun la quincena del mes."""
    if fecha is None:
        fecha = date.today()
    return 1 if fecha.day <= 15 else 2


def obtener_mes_quincena(fecha: date = None) -> tuple[int, int]:
    """Retorna (mes, quincena) para una fecha dada."""
    if fecha is None:
        fecha = date.today()
    return fecha.month, obtener_quincena(fecha)
