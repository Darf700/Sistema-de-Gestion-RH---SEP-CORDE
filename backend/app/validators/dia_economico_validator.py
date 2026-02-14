from datetime import date

from sqlalchemy.orm import Session

from ..config import settings
from ..models.contador import Contador
from ..schemas.justificante import ValidacionResponse
from ..services.calendario_service import calendario_service


def validar_dia_economico(
    db: Session,
    empleado_id: int,
    fecha_inicio: date,
    anio: int = None,
) -> ValidacionResponse:
    errores = []
    advertencias = []
    if anio is None:
        anio = fecha_inicio.year

    # 1. Verificar que sea dia laboral
    if not calendario_service.es_dia_laboral(fecha_inicio):
        errores.append("La fecha de inicio debe ser un dia laboral")

    # 2. Verificar que NO inicie en viernes (jueves o viernes no permitidos, solo Lun-Mie)
    dia_semana = fecha_inicio.weekday()  # 0=Lun ... 4=Vie
    if dia_semana > 2:  # Solo Lun(0), Mar(1), Mie(2)
        errores.append("El dia economico solo puede iniciar en Lunes, Martes o Miercoles")

    # 3. Verificar contadores
    contador = db.query(Contador).filter(
        Contador.empleado_id == empleado_id, Contador.anio == anio
    ).first()

    if contador:
        if contador.solicitudes_economicos >= settings.DIAS_ECONOMICOS_MAX_SOLICITUDES:
            errores.append(
                f"Ya se usaron las {settings.DIAS_ECONOMICOS_MAX_SOLICITUDES} solicitudes del anio"
            )

        # 4. Verificar 30 dias laborales desde ultima solicitud
        if contador.fecha_ultima_solicitud_economico:
            dias_desde_ultima = calendario_service.calcular_dias_laborales(
                contador.fecha_ultima_solicitud_economico, fecha_inicio
            )
            if dias_desde_ultima < settings.DIAS_ECONOMICOS_SEPARACION_DIAS:
                proxima = calendario_service.agregar_dias_laborales(
                    contador.fecha_ultima_solicitud_economico,
                    settings.DIAS_ECONOMICOS_SEPARACION_DIAS,
                )
                errores.append(
                    f"Deben pasar {settings.DIAS_ECONOMICOS_SEPARACION_DIAS} dias laborales "
                    f"desde la ultima solicitud. Proxima fecha disponible: {proxima}"
                )

    # 5. Verificar periodo bloqueado por vacaciones
    bloqueado, msg_vac = calendario_service.esta_en_periodo_bloqueado_vacaciones(
        fecha_inicio, dias_antes=settings.DIAS_ECONOMICOS_BLOQUEO_VACACIONES
    )
    if bloqueado:
        errores.append(msg_vac)

    # 6. Verificar cercanía a festivo
    cerca_festivo, msg_fest = calendario_service.esta_cerca_de_festivo(fecha_inicio)
    if cerca_festivo:
        errores.append(msg_fest)

    # 7. Calcular fecha fin (3 dias laborales consecutivos incluyendo inicio)
    fecha_fin = calendario_service.agregar_dias_laborales(fecha_inicio, 2)  # inicio + 2 mas

    return ValidacionResponse(
        valido=len(errores) == 0,
        errores=errores,
        advertencias=advertencias,
        fecha_inicio_calculada=fecha_inicio,
        fecha_fin_calculada=fecha_fin,
    )
