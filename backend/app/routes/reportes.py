from collections import Counter
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.adeudo import Adeudo, EstadoAdeudo
from ..models.contador import Contador
from ..models.empleado import Empleado
from ..models.justificante import EstadoJustificante, Justificante, TipoJustificante
from ..models.prestacion import Prestacion
from ..models.user import User
from ..schemas.reporte import (
    AdeudoReporteItem,
    AusentismoItem,
    DiasEconomicosItem,
    EstadisticaTipoItem,
    JustificantesReporteItem,
    PermisosHorasItem,
    PrestacionesReporteItem,
    ReporteAdeudosResponse,
    ReporteAusentismoResponse,
    ReporteDiasEconomicosResponse,
    ReporteEstadisticasResponse,
    ReporteJustificantesResponse,
    ReportePermisosHorasResponse,
    ReportePrestacionesResponse,
)
from ..services.export_service import generar_excel
from ..utils.dependencies import get_current_admin_user

router = APIRouter()

MAX_DIAS_ECONOMICOS = 3


# --- Helpers ---

def _formato_periodo(fi: date, ff: date) -> str:
    return f"{fi.isoformat()} a {ff.isoformat()}"


# --- 1. Ausentismo ---

@router.get("/ausentismo", response_model=ReporteAusentismoResponse)
def reporte_ausentismo(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    empleado_id: int = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Justificante, Empleado).join(
        Empleado, Justificante.empleado_id == Empleado.id
    ).filter(
        Justificante.fecha_inicio >= fecha_inicio,
        Justificante.fecha_fin <= fecha_fin,
    )
    if empleado_id:
        query = query.filter(Justificante.empleado_id == empleado_id)

    results = query.all()

    # Agrupar por empleado
    agrupado: dict[int, dict] = {}
    for just, emp in results:
        if emp.id not in agrupado:
            agrupado[emp.id] = {
                "empleado_id": emp.id,
                "nombre_completo": emp.nombre_completo,
                "total_ausencias": 0,
                "dias_economicos": 0,
                "permisos_horas": 0,
                "isstep": 0,
                "comisiones": 0,
            }
        item = agrupado[emp.id]
        item["total_ausencias"] += 1
        if just.tipo == TipoJustificante.DIA_ECONOMICO:
            item["dias_economicos"] += 1
        elif just.tipo == TipoJustificante.PERMISO_HORAS:
            item["permisos_horas"] += 1
        elif just.tipo == TipoJustificante.ISSTEP:
            item["isstep"] += 1
        elif just.tipo.value in ("Comision Todo el Dia", "Comision Entrada", "Comision Salida"):
            item["comisiones"] += 1

    datos = [AusentismoItem(**v) for v in agrupado.values()]
    return ReporteAusentismoResponse(
        datos=datos,
        total_registros=len(datos),
        periodo=_formato_periodo(fecha_inicio, fecha_fin),
    )


# --- 2. Dias Economicos ---

@router.get("/dias-economicos", response_model=ReporteDiasEconomicosResponse)
def reporte_dias_economicos(
    anio: int = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    anio = anio or date.today().year
    empleados = db.query(Empleado).filter(Empleado.activo == True).all()

    datos = []
    for emp in empleados:
        contador = db.query(Contador).filter(
            Contador.empleado_id == emp.id, Contador.anio == anio
        ).first()
        usados = contador.dias_economicos_usados if contador else 0
        solicitudes = contador.solicitudes_economicos if contador else 0
        fecha_ult = contador.fecha_ultima_solicitud_economico if contador else None
        datos.append(DiasEconomicosItem(
            empleado_id=emp.id,
            nombre_completo=emp.nombre_completo,
            dias_usados=usados,
            dias_disponibles=MAX_DIAS_ECONOMICOS - usados,
            solicitudes=solicitudes,
            fecha_ultima_solicitud=fecha_ult,
        ))

    return ReporteDiasEconomicosResponse(
        datos=datos, anio=anio, total_empleados=len(datos)
    )


# --- 3. Permisos por Horas ---

@router.get("/permisos-horas", response_model=ReportePermisosHorasResponse)
def reporte_permisos_horas(
    anio: int = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    anio = anio or date.today().year
    empleados = db.query(Empleado).filter(Empleado.activo == True).all()

    datos = []
    for emp in empleados:
        contador = db.query(Contador).filter(
            Contador.empleado_id == emp.id, Contador.anio == anio
        ).first()
        q1 = contador.permisos_horas_q1 if contador else 0
        q2 = contador.permisos_horas_q2 if contador else 0
        datos.append(PermisosHorasItem(
            empleado_id=emp.id,
            nombre_completo=emp.nombre_completo,
            permisos_q1=q1,
            permisos_q2=q2,
            total_permisos=q1 + q2,
        ))

    return ReportePermisosHorasResponse(
        datos=datos, anio=anio, total_empleados=len(datos)
    )


# --- 4. Prestaciones ---

@router.get("/prestaciones", response_model=ReportePrestacionesResponse)
def reporte_prestaciones(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    tipo: str = Query(None),
    estado: str = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Prestacion, Empleado).join(
        Empleado, Prestacion.empleado_id == Empleado.id
    ).filter(
        Prestacion.fecha_inicio >= fecha_inicio,
        Prestacion.fecha_fin <= fecha_fin,
    )
    if tipo:
        query = query.filter(Prestacion.tipo == tipo)
    if estado:
        query = query.filter(Prestacion.estado == estado)

    results = query.order_by(Prestacion.fecha_inicio.desc()).all()

    datos = []
    tipos_count: Counter = Counter()
    estados_count: Counter = Counter()
    for prest, emp in results:
        datos.append(PrestacionesReporteItem(
            id=prest.id,
            empleado_id=emp.id,
            nombre_completo=emp.nombre_completo,
            tipo=prest.tipo.value,
            fecha_inicio=prest.fecha_inicio,
            fecha_fin=prest.fecha_fin,
            dias_solicitados=prest.dias_solicitados,
            estado=prest.estado.value,
            fecha_solicitud=prest.fecha_solicitud,
        ))
        tipos_count[prest.tipo.value] += 1
        estados_count[prest.estado.value] += 1

    return ReportePrestacionesResponse(
        datos=datos,
        total_registros=len(datos),
        por_tipo=dict(tipos_count),
        por_estado=dict(estados_count),
    )


# --- 5. Justificantes ---

@router.get("/justificantes", response_model=ReporteJustificantesResponse)
def reporte_justificantes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    tipo: str = Query(None),
    empleado_id: int = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Justificante, Empleado).join(
        Empleado, Justificante.empleado_id == Empleado.id
    ).filter(
        Justificante.fecha_inicio >= fecha_inicio,
        Justificante.fecha_fin <= fecha_fin,
    )
    if tipo:
        query = query.filter(Justificante.tipo == tipo)
    if empleado_id:
        query = query.filter(Justificante.empleado_id == empleado_id)

    results = query.order_by(Justificante.fecha_inicio.desc()).all()

    datos = []
    tipos_count: Counter = Counter()
    estados_count: Counter = Counter()
    for just, emp in results:
        datos.append(JustificantesReporteItem(
            id=just.id,
            empleado_id=emp.id,
            nombre_completo=emp.nombre_completo,
            tipo=just.tipo.value,
            fecha_inicio=just.fecha_inicio,
            fecha_fin=just.fecha_fin,
            dias_solicitados=just.dias_solicitados,
            estado=just.estado.value,
            fecha_generacion=just.fecha_generacion,
        ))
        tipos_count[just.tipo.value] += 1
        estados_count[just.estado.value] += 1

    return ReporteJustificantesResponse(
        datos=datos,
        total_registros=len(datos),
        por_tipo=dict(tipos_count),
        por_estado=dict(estados_count),
    )


# --- 6. Adeudos ---

@router.get("/adeudos", response_model=ReporteAdeudosResponse)
def reporte_adeudos(
    estado: str = Query("Pendiente"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Adeudo, Empleado).join(
        Empleado, Adeudo.empleado_id == Empleado.id
    )
    if estado:
        query = query.filter(Adeudo.estado == estado)

    results = query.order_by(Adeudo.fecha_marcado.desc()).all()

    datos = []
    total_dias = 0
    for adeudo, emp in results:
        datos.append(AdeudoReporteItem(
            id=adeudo.id,
            empleado_id=emp.id,
            nombre_completo=emp.nombre_completo,
            tipo=adeudo.tipo,
            descripcion=adeudo.descripcion,
            dias_debe=adeudo.dias_debe or 0,
            justificante_id=adeudo.justificante_id,
            estado=adeudo.estado.value,
            fecha_marcado=adeudo.fecha_marcado,
        ))
        if adeudo.estado == EstadoAdeudo.PENDIENTE:
            total_dias += adeudo.dias_debe or 0

    return ReporteAdeudosResponse(
        datos=datos,
        total_registros=len(datos),
        total_dias_pendientes=total_dias,
    )


# --- 7. Extemporaneos ---

@router.get("/extemporaneos", response_model=ReporteJustificantesResponse)
def reporte_extemporaneos(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    results = db.query(Justificante, Empleado).join(
        Empleado, Justificante.empleado_id == Empleado.id
    ).filter(
        Justificante.estado == EstadoJustificante.EXTEMPORANEO,
        Justificante.fecha_inicio >= fecha_inicio,
        Justificante.fecha_fin <= fecha_fin,
    ).order_by(Justificante.fecha_inicio.desc()).all()

    datos = []
    tipos_count: Counter = Counter()
    for just, emp in results:
        datos.append(JustificantesReporteItem(
            id=just.id,
            empleado_id=emp.id,
            nombre_completo=emp.nombre_completo,
            tipo=just.tipo.value,
            fecha_inicio=just.fecha_inicio,
            fecha_fin=just.fecha_fin,
            dias_solicitados=just.dias_solicitados,
            estado=just.estado.value,
            fecha_generacion=just.fecha_generacion,
        ))
        tipos_count[just.tipo.value] += 1

    return ReporteJustificantesResponse(
        datos=datos,
        total_registros=len(datos),
        por_tipo=dict(tipos_count),
        por_estado={"Extemporaneo": len(datos)},
    )


# --- 8. Estadisticas Justificantes ---

@router.get("/estadisticas-justificantes", response_model=ReporteEstadisticasResponse)
def reporte_estadisticas_justificantes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    justificantes = db.query(Justificante).filter(
        Justificante.fecha_inicio >= fecha_inicio,
        Justificante.fecha_fin <= fecha_fin,
    ).all()

    tipo_count: Counter = Counter()
    estado_count: Counter = Counter()
    for j in justificantes:
        tipo_count[j.tipo.value] += 1
        estado_count[j.estado.value] += 1

    datos = []
    for val, cnt in tipo_count.items():
        datos.append(EstadisticaTipoItem(categoria="Tipo", valor=val, conteo=cnt))
    for val, cnt in estado_count.items():
        datos.append(EstadisticaTipoItem(categoria="Estado", valor=val, conteo=cnt))

    return ReporteEstadisticasResponse(
        datos=datos,
        total_justificantes=len(justificantes),
        periodo=_formato_periodo(fecha_inicio, fecha_fin),
    )


# --- 9. Export Excel ---

EXPORT_CONFIGS = {
    "ausentismo": {
        "titulo": "Reporte de Ausentismo",
        "columnas": ["Empleado", "Total Ausencias", "Dias Economicos", "Permisos Horas", "ISSTEP", "Comisiones"],
        "campos": ["nombre_completo", "total_ausencias", "dias_economicos", "permisos_horas", "isstep", "comisiones"],
    },
    "dias-economicos": {
        "titulo": "Reporte de Dias Economicos",
        "columnas": ["Empleado", "Dias Usados", "Dias Disponibles", "Solicitudes", "Ultima Solicitud"],
        "campos": ["nombre_completo", "dias_usados", "dias_disponibles", "solicitudes", "fecha_ultima_solicitud"],
    },
    "permisos-horas": {
        "titulo": "Reporte de Permisos por Horas",
        "columnas": ["Empleado", "Permisos Q1", "Permisos Q2", "Total Permisos"],
        "campos": ["nombre_completo", "permisos_q1", "permisos_q2", "total_permisos"],
    },
    "prestaciones": {
        "titulo": "Reporte de Prestaciones",
        "columnas": ["Empleado", "Tipo", "Fecha Inicio", "Fecha Fin", "Dias", "Estado", "Fecha Solicitud"],
        "campos": ["nombre_completo", "tipo", "fecha_inicio", "fecha_fin", "dias_solicitados", "estado", "fecha_solicitud"],
    },
    "justificantes": {
        "titulo": "Reporte de Justificantes",
        "columnas": ["Empleado", "Tipo", "Fecha Inicio", "Fecha Fin", "Dias", "Estado", "Fecha Generacion"],
        "campos": ["nombre_completo", "tipo", "fecha_inicio", "fecha_fin", "dias_solicitados", "estado", "fecha_generacion"],
    },
    "adeudos": {
        "titulo": "Reporte de Adeudos",
        "columnas": ["Empleado", "Tipo", "Descripcion", "Dias", "Estado", "Fecha"],
        "campos": ["nombre_completo", "tipo", "descripcion", "dias_debe", "estado", "fecha_marcado"],
    },
    "extemporaneos": {
        "titulo": "Reporte de Extemporaneos",
        "columnas": ["Empleado", "Tipo", "Fecha Inicio", "Fecha Fin", "Dias", "Fecha Generacion"],
        "campos": ["nombre_completo", "tipo", "fecha_inicio", "fecha_fin", "dias_solicitados", "fecha_generacion"],
    },
    "estadisticas-justificantes": {
        "titulo": "Estadisticas de Justificantes",
        "columnas": ["Categoria", "Valor", "Conteo"],
        "campos": ["categoria", "valor", "conteo"],
    },
}


@router.get("/export")
def exportar_reporte(
    reporte: str = Query(...),
    fecha_inicio: date = Query(None),
    fecha_fin: date = Query(None),
    anio: int = Query(None),
    tipo: str = Query(None),
    estado: str = Query(None),
    empleado_id: int = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if reporte not in EXPORT_CONFIGS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Reporte '{reporte}' no valido")

    config = EXPORT_CONFIGS[reporte]

    # Obtener datos llamando al endpoint correspondiente
    handlers = {
        "ausentismo": lambda: reporte_ausentismo(fecha_inicio, fecha_fin, empleado_id, current_user, db),
        "dias-economicos": lambda: reporte_dias_economicos(anio, current_user, db),
        "permisos-horas": lambda: reporte_permisos_horas(anio, current_user, db),
        "prestaciones": lambda: reporte_prestaciones(fecha_inicio, fecha_fin, tipo, estado, current_user, db),
        "justificantes": lambda: reporte_justificantes(fecha_inicio, fecha_fin, tipo, empleado_id, current_user, db),
        "adeudos": lambda: reporte_adeudos(estado, current_user, db),
        "extemporaneos": lambda: reporte_extemporaneos(fecha_inicio, fecha_fin, current_user, db),
        "estadisticas-justificantes": lambda: reporte_estadisticas_justificantes(fecha_inicio, fecha_fin, current_user, db),
    }

    resultado = handlers[reporte]()
    items = resultado.datos

    # Convertir a filas
    filas = []
    for item in items:
        fila = []
        for campo in config["campos"]:
            val = getattr(item, campo, "")
            if isinstance(val, (date, datetime)):
                val = val.isoformat()
            elif val is None:
                val = ""
            fila.append(val)
        filas.append(fila)

    excel_file = generar_excel(config["titulo"], config["columnas"], filas)
    filename = f"{reporte}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
