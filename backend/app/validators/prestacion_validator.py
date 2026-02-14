from datetime import date

from sqlalchemy.orm import Session

from ..models.contador import Contador
from ..models.empleado import Empleado, TipoEmpleado, TipoNombramiento
from ..models.prestacion import Prestacion, TipoPrestacion, EstadoPrestacion
from ..schemas.prestacion import PrestacionValidacionResponse
from ..services.calendario_service import calendario_service

# Catalogo de prestaciones con sus reglas
CATALOGO_PRESTACIONES = {
    TipoPrestacion.LICENCIA_MEDICA: {
        "nombre": "Licencia Medica",
        "descripcion": "Licencia por enfermedad con dictamen medico del ISSTEP",
        "dias_maximos": None,  # Segun dictamen
        "documentos_requeridos": ["Dictamen medico ISSTEP"],
        "requisitos": ["Antiguedad minima de 6 meses + 1 dia"],
    },
    TipoPrestacion.CUIDADOS_MATERNOS: {
        "nombre": "Cuidados Maternos/Paternos",
        "descripcion": "Para hijos de hasta 8 anios 11 meses",
        "dias_maximos": 7,
        "documentos_requeridos": [
            "Dictamen medico ISSTEP",
            "Acta de nacimiento del hijo",
            "Carnet ISSTEP",
        ],
        "requisitos": [
            "Antiguedad minima de 6 meses + 1 dia",
            "Hijos hasta 8 anios 11 meses",
            "Maximo 7 dias habiles por anio natural",
        ],
    },
    TipoPrestacion.CUIDADOS_MEDICOS_FAMILIARES: {
        "nombre": "Cuidados Medicos Familiares",
        "descripcion": "Para conyuge, padres o hijos dependientes economicamente",
        "dias_maximos": 14,  # Docente=14, Apoyo=12, se ajusta en validacion
        "documentos_requeridos": [
            "Dictamen medico ISSTEP",
            "Comprobante de parentesco",
        ],
        "requisitos": [
            "Antiguedad minima de 6 meses + 1 dia",
            "Apoyo/Asistencia: max 12 dias habiles/anio",
            "Docente: max 14 dias habiles/anio",
        ],
    },
    TipoPrestacion.FALLECIMIENTO_FAMILIAR: {
        "nombre": "Permiso por Fallecimiento de Familiar",
        "descripcion": "Para hijos, conyuge, padres o hermanos",
        "dias_maximos": 6,  # Basica=5, Media/Superior=6
        "documentos_requeridos": ["Acta de defuncion"],
        "requisitos": [
            "Familiar: Hijos, Conyuge, Padres, Hermanos",
            "Basica: hasta 5 dias habiles",
            "Media Superior/Superior: hasta 6 dias habiles",
        ],
    },
    TipoPrestacion.MEDIA_HORA_TOLERANCIA: {
        "nombre": "Media Hora de Tolerancia",
        "descripcion": "Para padres con hijos en lactantes, maternal, preescolar o primaria",
        "dias_maximos": None,  # Vigencia del ciclo escolar
        "documentos_requeridos": [
            "Constancia de estudios",
            "Acta de nacimiento del hijo",
            "Boucher de inscripcion",
        ],
        "requisitos": [
            "Diferencia de traslado > 10 minutos",
            "Entrada escuela = entrada trabajo (8:00 AM)",
            "Suspendido en periodos vacacionales y receso escolar",
        ],
    },
    TipoPrestacion.LICENCIA_NUPCIAS: {
        "nombre": "Licencia por Nupcias",
        "descripcion": "5 dias habiles con goce de sueldo",
        "dias_maximos": 5,
        "documentos_requeridos": ["Acta de matrimonio"],
        "requisitos": ["Antiguedad minima de 6 meses + 1 dia"],
    },
    TipoPrestacion.LICENCIA_PATERNIDAD: {
        "nombre": "Licencia por Paternidad",
        "descripcion": "6 dias con goce de sueldo por nacimiento o adopcion",
        "dias_maximos": 6,
        "documentos_requeridos": [
            "Constancia de concubinato o alumbramiento",
            "Acta de nacimiento o adopcion",
        ],
        "requisitos": ["Antiguedad minima de 6 meses + 1 dia"],
    },
}

# Nombramientos que NO pueden acceder a prestaciones
NOMBRAMIENTOS_EXCLUIDOS = {
    TipoNombramiento.INTERINO,
    TipoNombramiento.LIMITADO,
    TipoNombramiento.GRAVIDEZ,
    TipoNombramiento.PREJUBILATORIO,
    TipoNombramiento.HONORARIOS,
}


def validar_prestacion(
    db: Session,
    empleado: Empleado,
    tipo: TipoPrestacion,
    fecha_inicio: date,
    fecha_fin: date,
    dias_solicitados: int = None,
) -> PrestacionValidacionResponse:
    errores = []
    advertencias = []
    catalogo = CATALOGO_PRESTACIONES.get(tipo, {})

    # 1. Validar nombramiento
    if empleado.nombramiento in NOMBRAMIENTOS_EXCLUIDOS:
        errores.append(
            f"No aplica para empleados con nombramiento: {empleado.nombramiento.value}"
        )

    # 2. Validar antiguedad
    if not empleado.cumple_antiguedad_minima:
        errores.append(
            f"Antiguedad insuficiente ({empleado.antiguedad_meses} meses). "
            "Se requieren 6 meses + 1 dia."
        )

    # 3. Validar fechas
    if fecha_inicio > fecha_fin:
        errores.append("La fecha de inicio debe ser anterior a la fecha de fin")

    # 4. Calcular dias laborales
    dias_lab = calendario_service.calcular_dias_laborales(fecha_inicio, fecha_fin)
    if dias_solicitados and dias_solicitados != dias_lab:
        advertencias.append(
            f"Dias solicitados ({dias_solicitados}) difiere de dias laborales calculados ({dias_lab})"
        )

    # 5. Validar dias maximos segun tipo
    dias_max = catalogo.get("dias_maximos")
    if tipo == TipoPrestacion.CUIDADOS_MEDICOS_FAMILIARES:
        dias_max = 12 if empleado.tipo == TipoEmpleado.APOYO else 14

    if tipo == TipoPrestacion.FALLECIMIENTO_FAMILIAR:
        dias_max = 5 if empleado.tipo == TipoEmpleado.APOYO else 6

    if dias_max and dias_lab > dias_max:
        errores.append(f"Excede el maximo de {dias_max} dias habiles para este tipo de prestacion")

    # 6. Validar contadores anuales para tipos acumulables
    anio = fecha_inicio.year
    contador = db.query(Contador).filter(
        Contador.empleado_id == empleado.id, Contador.anio == anio
    ).first()

    if tipo == TipoPrestacion.CUIDADOS_MATERNOS and contador:
        usado = contador.cuidados_maternos_usados
        if usado + dias_lab > 7:
            errores.append(
                f"Excede el limite anual. Usado: {usado} dias, solicitando: {dias_lab}, maximo: 7"
            )

    if tipo == TipoPrestacion.CUIDADOS_MEDICOS_FAMILIARES and contador:
        usado = contador.cuidados_medicos_usados
        limite = 12 if empleado.tipo == TipoEmpleado.APOYO else 14
        if usado + dias_lab > limite:
            errores.append(
                f"Excede el limite anual. Usado: {usado} dias, solicitando: {dias_lab}, maximo: {limite}"
            )

    # 7. Verificar si ya tiene prestacion activa del mismo tipo en el periodo
    prestacion_existente = (
        db.query(Prestacion)
        .filter(
            Prestacion.empleado_id == empleado.id,
            Prestacion.tipo == tipo,
            Prestacion.estado != EstadoPrestacion.RECHAZADA,
            Prestacion.fecha_inicio <= fecha_fin,
            Prestacion.fecha_fin >= fecha_inicio,
        )
        .first()
    )
    if prestacion_existente:
        errores.append("Ya existe una prestacion del mismo tipo en este periodo")

    return PrestacionValidacionResponse(
        valido=len(errores) == 0,
        errores=errores,
        advertencias=advertencias,
        documentos_requeridos=catalogo.get("documentos_requeridos", []),
        dias_maximos=dias_max,
    )
