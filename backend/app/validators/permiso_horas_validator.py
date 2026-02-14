from datetime import date

from sqlalchemy.orm import Session

from ..config import settings
from ..models.justificante import Justificante, TipoJustificante
from ..schemas.justificante import ValidacionResponse
from ..services.calendario_service import calendario_service
from ..utils.helpers import obtener_quincena


def validar_permiso_horas(
    db: Session,
    empleado_id: int,
    fecha: date,
) -> ValidacionResponse:
    errores = []
    advertencias = []

    # 1. Verificar dia laboral
    if not calendario_service.es_dia_laboral(fecha):
        errores.append("La fecha debe ser un dia laboral")

    # 2. Contar permisos en la quincena actual
    quincena = obtener_quincena(fecha)
    if quincena == 1:
        inicio_q = date(fecha.year, fecha.month, 1)
        fin_q = date(fecha.year, fecha.month, 15)
    else:
        inicio_q = date(fecha.year, fecha.month, 16)
        # Fin de mes
        if fecha.month == 12:
            fin_q = date(fecha.year, 12, 31)
        else:
            fin_q = date(fecha.year, fecha.month + 1, 1)
            from datetime import timedelta
            fin_q -= timedelta(days=1)

    permisos_quincena = (
        db.query(Justificante)
        .filter(
            Justificante.empleado_id == empleado_id,
            Justificante.tipo == TipoJustificante.PERMISO_HORAS,
            Justificante.fecha_inicio >= inicio_q,
            Justificante.fecha_inicio <= fin_q,
        )
        .count()
    )

    if permisos_quincena >= settings.PERMISOS_HORAS_MAX_POR_QUINCENA:
        errores.append(
            f"Ya se usaron los {settings.PERMISOS_HORAS_MAX_POR_QUINCENA} "
            f"permisos por horas de la quincena {quincena} "
            f"({inicio_q} a {fin_q})"
        )

    return ValidacionResponse(
        valido=len(errores) == 0,
        errores=errores,
        advertencias=advertencias,
        fecha_inicio_calculada=fecha,
        fecha_fin_calculada=fecha,
    )
