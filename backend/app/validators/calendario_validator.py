from datetime import date

from ..services.calendario_service import calendario_service


def validar_fecha_laboral(fecha: date) -> tuple[bool, str]:
    if not calendario_service.es_dia_laboral(fecha):
        if calendario_service.es_fin_de_semana(fecha):
            return False, "La fecha cae en fin de semana"
        if calendario_service.es_festivo(fecha):
            return False, "La fecha es dia festivo oficial"
        if calendario_service.esta_en_vacaciones(fecha):
            return False, "La fecha cae en periodo de vacaciones"
    return True, ""
