"""Servicio de generacion de PDFs para justificantes y prestaciones."""
import os
from datetime import date, time
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..config import settings

# ─── Constantes ────────────────────────────────────────────────────────────────

MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points

# Colores del estado
ESTADO_COLORS = {
    "Generado": colors.HexColor("#2563EB"),
    "Entregado": colors.HexColor("#16A34A"),
    "Extemporaneo": colors.HexColor("#D97706"),
    "Pendiente": colors.HexColor("#D97706"),
    "Aprobada": colors.HexColor("#16A34A"),
    "Rechazada": colors.HexColor("#DC2626"),
}


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _fecha_larga(fecha: date) -> str:
    """Convierte date a formato largo: 'Cuatro veces Heroica Puebla de Zaragoza, a 15 de enero de 2026'."""
    return (
        f"Cuatro veces Heroica Puebla de Zaragoza, a {fecha.day} "
        f"de {MESES[fecha.month]} de {fecha.year}"
    )


def _hora_str(t: time | None) -> str:
    """Formatea time a HH:MM."""
    if t is None:
        return ""
    return t.strftime("%H:%M")


def _dibujar_encabezado(elements, styles, codigo_formato: str):
    """Dibuja el encabezado institucional del formato."""
    # Codigo de formato (esquina derecha)
    elements.append(Paragraph(
        f'<para align="right"><b>{codigo_formato}</b></para>',
        styles["codigo_formato"],
    ))
    elements.append(Spacer(1, 4 * mm))

    # Titulo institucional
    elements.append(Paragraph(
        f'<para align="center"><b>{settings.PDF_INSTITUCION}</b></para>',
        styles["titulo"],
    ))
    elements.append(Paragraph(
        f'<para align="center"><b>{settings.PDF_COORDINACION}</b></para>',
        styles["subtitulo"],
    ))
    elements.append(Paragraph(
        f'<para align="center"><b>{settings.PDF_INMUEBLE}</b></para>',
        styles["subtitulo"],
    ))
    elements.append(Spacer(1, 8 * mm))


def _dibujar_firmas(elements, styles):
    """Dibuja la seccion de firmas al final del documento."""
    elements.append(Spacer(1, 20 * mm))

    firma_style = ParagraphStyle(
        "firma_texto", parent=styles["Normal"],
        fontSize=8, alignment=1, leading=10,
    )

    firma_data = [
        [
            Paragraph("<b>Vo. Bo. Jefe Inmediato</b>", firma_style),
            Paragraph("<b>Autorizo Titular</b>", firma_style),
            Paragraph("<b>Recibido RH</b>", firma_style),
        ],
        [
            Paragraph("_" * 28, firma_style),
            Paragraph("_" * 28, firma_style),
            Paragraph("_" * 28, firma_style),
        ],
        [
            Paragraph("Nombre y firma", firma_style),
            Paragraph("Nombre y firma", firma_style),
            Paragraph("Nombre, firma y sello", firma_style),
        ],
    ]

    firma_table = Table(firma_data, colWidths=[6 * cm, 6 * cm, 6 * cm])
    firma_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(firma_table)


def _dibujar_checkbox(marcado: bool) -> str:
    """Retorna representacion de checkbox como texto."""
    return "[X]" if marcado else "[  ]"


def _get_styles():
    """Crea y retorna los estilos para el PDF."""
    base = getSampleStyleSheet()

    custom_styles = {
        "Normal": base["Normal"],
        "codigo_formato": ParagraphStyle(
            "codigo_formato", parent=base["Normal"],
            fontSize=9, textColor=colors.gray,
        ),
        "titulo": ParagraphStyle(
            "titulo", parent=base["Normal"],
            fontSize=13, alignment=1, spaceAfter=2 * mm,
            fontName="Helvetica-Bold",
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", parent=base["Normal"],
            fontSize=10, alignment=1, spaceAfter=1 * mm,
            fontName="Helvetica-Bold",
        ),
        "fecha": ParagraphStyle(
            "fecha", parent=base["Normal"],
            fontSize=9, alignment=2, spaceAfter=4 * mm,
        ),
        "campo_label": ParagraphStyle(
            "campo_label", parent=base["Normal"],
            fontSize=9, fontName="Helvetica-Bold",
        ),
        "campo_valor": ParagraphStyle(
            "campo_valor", parent=base["Normal"],
            fontSize=9,
        ),
        "tipo_titulo": ParagraphStyle(
            "tipo_titulo", parent=base["Normal"],
            fontSize=11, fontName="Helvetica-Bold",
            alignment=1, spaceBefore=4 * mm, spaceAfter=4 * mm,
        ),
        "estado_badge": ParagraphStyle(
            "estado_badge", parent=base["Normal"],
            fontSize=9, alignment=1,
        ),
        "nota": ParagraphStyle(
            "nota", parent=base["Normal"],
            fontSize=7, textColor=colors.gray,
            alignment=1, spaceBefore=6 * mm,
        ),
    }
    return custom_styles


def _dibujar_datos_empleado(elements, styles, empleado):
    """Dibuja la tabla de datos del empleado."""
    cell_style = styles["campo_valor"]
    label_style = styles["campo_label"]

    data = [
        [
            Paragraph("<b>Nombre:</b>", label_style),
            Paragraph(empleado.nombre_completo, cell_style),
            Paragraph("<b>No. Asistencia:</b>", label_style),
            Paragraph(empleado.numero_asistencia, cell_style),
        ],
        [
            Paragraph("<b>Horario:</b>", label_style),
            Paragraph(empleado.horario, cell_style),
            Paragraph("<b>Tipo:</b>", label_style),
            Paragraph(empleado.tipo.value if hasattr(empleado.tipo, 'value') else str(empleado.tipo), cell_style),
        ],
        [
            Paragraph("<b>Clave(s):</b>", label_style),
            Paragraph(empleado.claves_presupuestales, cell_style),
            Paragraph("<b>Adscripcion:</b>", label_style),
            Paragraph(empleado.adscripcion, cell_style),
        ],
    ]

    t = Table(data, colWidths=[3 * cm, 6.5 * cm, 3.5 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (1, 0), (1, -1), 0.5, colors.gray),
        ("LINEBELOW", (3, 0), (3, -1), 0.5, colors.gray),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 4 * mm))


def _dibujar_estado(elements, styles, estado: str):
    """Dibuja badge del estado."""
    color = ESTADO_COLORS.get(estado, colors.gray)
    elements.append(Paragraph(
        f'<para align="center"><font color="{color.hexval()}"><b>Estado: {estado}</b></font></para>',
        styles["estado_badge"],
    ))


# ─── Generadores principales ──────────────────────────────────────────────────

def generar_pdf_justificante(
    justificante,
    empleado,
) -> BytesIO:
    """Genera PDF de justificante. Retorna BytesIO con el contenido."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = _get_styles()
    elements = []

    # Encabezado
    _dibujar_encabezado(elements, styles, "F/004")

    # Titulo del formato
    elements.append(Paragraph(
        '<para align="center"><b>FORMATO DE JUSTIFICANTE DE INASISTENCIA</b></para>',
        styles["tipo_titulo"],
    ))

    # Fecha
    fecha_gen = justificante.fecha_generacion or justificante.created_at.date() if hasattr(justificante.created_at, 'date') else date.today()
    if isinstance(fecha_gen, date):
        elements.append(Paragraph(_fecha_larga(fecha_gen), styles["fecha"]))
    elements.append(Spacer(1, 4 * mm))

    # Datos del empleado
    _dibujar_datos_empleado(elements, styles, empleado)

    # Tipo de justificante (checkboxes)
    from ..models.justificante import TipoJustificante
    tipos_list = list(TipoJustificante)

    checkbox_data = []
    row = []
    for i, tipo in enumerate(tipos_list):
        cb = _dibujar_checkbox(justificante.tipo == tipo or justificante.tipo.value == tipo.value)
        row.append(Paragraph(f"{cb} {tipo.value}", styles["campo_valor"]))
        if (i + 1) % 3 == 0 or i == len(tipos_list) - 1:
            while len(row) < 3:
                row.append(Paragraph("", styles["campo_valor"]))
            checkbox_data.append(row)
            row = []

    if checkbox_data:
        cb_table = Table(checkbox_data, colWidths=[6 * cm, 6 * cm, 6 * cm])
        cb_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(Paragraph("<b>Tipo de justificante:</b>", styles["campo_label"]))
        elements.append(Spacer(1, 2 * mm))
        elements.append(cb_table)
        elements.append(Spacer(1, 4 * mm))

    # Detalles segun tipo
    detalles = []

    detalles.append([
        Paragraph("<b>Fecha inicio:</b>", styles["campo_label"]),
        Paragraph(str(justificante.fecha_inicio), styles["campo_valor"]),
        Paragraph("<b>Fecha fin:</b>", styles["campo_label"]),
        Paragraph(str(justificante.fecha_fin), styles["campo_valor"]),
    ])

    if justificante.dias_solicitados:
        detalles.append([
            Paragraph("<b>Dias solicitados:</b>", styles["campo_label"]),
            Paragraph(str(justificante.dias_solicitados), styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
        ])

    tipo_val = justificante.tipo.value if hasattr(justificante.tipo, 'value') else str(justificante.tipo)

    if "Comision" in tipo_val and justificante.lugar:
        detalles.append([
            Paragraph("<b>Lugar de comision:</b>", styles["campo_label"]),
            Paragraph(justificante.lugar, styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
        ])

    if tipo_val == "Permiso por Horas":
        detalles.append([
            Paragraph("<b>Hora inicio:</b>", styles["campo_label"]),
            Paragraph(_hora_str(justificante.hora_inicio), styles["campo_valor"]),
            Paragraph("<b>Hora fin:</b>", styles["campo_label"]),
            Paragraph(_hora_str(justificante.hora_fin), styles["campo_valor"]),
        ])

    if justificante.motivo:
        detalles.append([
            Paragraph("<b>Motivo:</b>", styles["campo_label"]),
            Paragraph(justificante.motivo, styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
        ])

    if detalles:
        det_table = Table(detalles, colWidths=[3.5 * cm, 5.5 * cm, 3.5 * cm, 5.5 * cm])
        det_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBELOW", (1, 0), (1, -1), 0.5, colors.gray),
            ("LINEBELOW", (3, 0), (3, -1), 0.5, colors.gray),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        elements.append(det_table)

    # Estado
    elements.append(Spacer(1, 6 * mm))
    estado_val = justificante.estado.value if hasattr(justificante.estado, 'value') else str(justificante.estado)
    _dibujar_estado(elements, styles, estado_val)

    # Firmas
    _dibujar_firmas(elements, styles)

    # Nota al pie
    elements.append(Paragraph(
        "Este documento debe ser firmado y entregado a Recursos Humanos dentro de los 3 dias habiles posteriores.",
        styles["nota"],
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_pdf_prestacion(
    prestacion,
    empleado,
) -> BytesIO:
    """Genera PDF de prestacion. Retorna BytesIO con el contenido."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = _get_styles()
    elements = []

    # Encabezado
    _dibujar_encabezado(elements, styles, "F/005")

    # Titulo del formato
    elements.append(Paragraph(
        '<para align="center"><b>FORMATO DE SOLICITUD DE PRESTACION</b></para>',
        styles["tipo_titulo"],
    ))

    # Fecha
    fecha_sol = prestacion.fecha_solicitud or date.today()
    if isinstance(fecha_sol, date):
        elements.append(Paragraph(_fecha_larga(fecha_sol), styles["fecha"]))
    elements.append(Spacer(1, 4 * mm))

    # Datos del empleado
    _dibujar_datos_empleado(elements, styles, empleado)

    # Tipo de prestacion (checkboxes)
    from ..models.prestacion import TipoPrestacion
    tipos_list = list(TipoPrestacion)

    checkbox_data = []
    row = []
    for i, tipo in enumerate(tipos_list):
        cb = _dibujar_checkbox(prestacion.tipo == tipo or prestacion.tipo.value == tipo.value)
        row.append(Paragraph(f"{cb} {tipo.value}", styles["campo_valor"]))
        if (i + 1) % 2 == 0 or i == len(tipos_list) - 1:
            while len(row) < 2:
                row.append(Paragraph("", styles["campo_valor"]))
            checkbox_data.append(row)
            row = []

    if checkbox_data:
        cb_table = Table(checkbox_data, colWidths=[9 * cm, 9 * cm])
        cb_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(Paragraph("<b>Tipo de prestacion:</b>", styles["campo_label"]))
        elements.append(Spacer(1, 2 * mm))
        elements.append(cb_table)
        elements.append(Spacer(1, 4 * mm))

    # Detalles
    detalles = [
        [
            Paragraph("<b>Fecha inicio:</b>", styles["campo_label"]),
            Paragraph(str(prestacion.fecha_inicio), styles["campo_valor"]),
            Paragraph("<b>Fecha fin:</b>", styles["campo_label"]),
            Paragraph(str(prestacion.fecha_fin), styles["campo_valor"]),
        ],
    ]

    if prestacion.dias_solicitados:
        detalles.append([
            Paragraph("<b>Dias solicitados:</b>", styles["campo_label"]),
            Paragraph(str(prestacion.dias_solicitados), styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
        ])

    if prestacion.motivo:
        detalles.append([
            Paragraph("<b>Motivo:</b>", styles["campo_label"]),
            Paragraph(prestacion.motivo, styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
            Paragraph("", styles["campo_valor"]),
        ])

    det_table = Table(detalles, colWidths=[3.5 * cm, 5.5 * cm, 3.5 * cm, 5.5 * cm])
    det_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (1, 0), (1, -1), 0.5, colors.gray),
        ("LINEBELOW", (3, 0), (3, -1), 0.5, colors.gray),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    elements.append(det_table)

    # Estado
    elements.append(Spacer(1, 6 * mm))
    estado_val = prestacion.estado.value if hasattr(prestacion.estado, 'value') else str(prestacion.estado)
    _dibujar_estado(elements, styles, estado_val)

    # Firmas
    _dibujar_firmas(elements, styles)

    # Nota
    elements.append(Paragraph(
        "Este documento debe ser firmado y entregado a Recursos Humanos junto con la documentacion requerida.",
        styles["nota"],
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def guardar_pdf(buffer: BytesIO, subdir: str, filename: str) -> str:
    """Guarda un PDF en disco y retorna la ruta relativa."""
    dir_path = os.path.join(settings.PDF_DIR, subdir)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, filename)
    with open(file_path, "wb") as f:
        f.write(buffer.read())
    buffer.seek(0)
    return file_path
