from datetime import date, timedelta
from typing import List, Tuple

from ..config import settings


class CalendarioService:
    """Servicio para manejo de calendario laboral."""

    def __init__(self):
        self._festivos_cache: dict[int, List[date]] = {}
        self._vacaciones_cache: List[Tuple[date, date]] = []
        self._cargar_vacaciones()

    def _cargar_festivos(self, anio: int) -> List[date]:
        if anio in self._festivos_cache:
            return self._festivos_cache[anio]

        if anio == 2026:
            festivos = [date(2026, m, d) for m, d in settings.FESTIVOS_2026]
        elif anio == 2025:
            festivos = [
                date(2025, 1, 1),
                date(2025, 2, 3),
                date(2025, 3, 17),
                date(2025, 5, 1),
                date(2025, 9, 16),
                date(2025, 11, 17),
                date(2025, 12, 25),
            ]
        else:
            # Festivos fijos + calcular lunes moviles
            festivos = [
                date(anio, 1, 1),
                date(anio, 5, 1),
                date(anio, 9, 16),
                date(anio, 12, 25),
            ]
            # Primer lunes de febrero
            d = date(anio, 2, 1)
            while d.weekday() != 0:
                d += timedelta(days=1)
            festivos.append(d)
            # Tercer lunes de marzo
            d = date(anio, 3, 1)
            count = 0
            while count < 3:
                if d.weekday() == 0:
                    count += 1
                    if count == 3:
                        break
                d += timedelta(days=1)
            festivos.append(d)
            # Tercer lunes de noviembre
            d = date(anio, 11, 1)
            count = 0
            while count < 3:
                if d.weekday() == 0:
                    count += 1
                    if count == 3:
                        break
                d += timedelta(days=1)
            festivos.append(d)

        self._festivos_cache[anio] = festivos
        return festivos

    def _cargar_vacaciones(self):
        self._vacaciones_cache = []
        for inicio_str, fin_str in settings.VACACIONES_2026:
            inicio = date.fromisoformat(inicio_str)
            fin = date.fromisoformat(fin_str)
            self._vacaciones_cache.append((inicio, fin))

    def es_fin_de_semana(self, fecha: date) -> bool:
        return fecha.weekday() >= 5

    def es_festivo(self, fecha: date) -> bool:
        festivos = self._cargar_festivos(fecha.year)
        return fecha in festivos

    def esta_en_vacaciones(self, fecha: date) -> bool:
        for inicio, fin in self._vacaciones_cache:
            if inicio <= fecha <= fin:
                return True
        return False

    def es_dia_laboral(self, fecha: date) -> bool:
        if self.es_fin_de_semana(fecha):
            return False
        if self.es_festivo(fecha):
            return False
        if self.esta_en_vacaciones(fecha):
            return False
        return True

    def calcular_dias_laborales(self, fecha_inicio: date, fecha_fin: date) -> int:
        """Cuenta dias laborales entre dos fechas (inclusivo)."""
        if fecha_inicio > fecha_fin:
            return 0
        dias = 0
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            if self.es_dia_laboral(fecha_actual):
                dias += 1
            fecha_actual += timedelta(days=1)
        return dias

    def agregar_dias_laborales(self, fecha_inicio: date, num_dias: int) -> date:
        """Suma N dias laborales a una fecha."""
        fecha_actual = fecha_inicio
        dias_contados = 0
        while dias_contados < num_dias:
            fecha_actual += timedelta(days=1)
            if self.es_dia_laboral(fecha_actual):
                dias_contados += 1
        return fecha_actual

    def restar_dias_laborales(self, fecha_inicio: date, num_dias: int) -> date:
        """Resta N dias laborales a una fecha."""
        fecha_actual = fecha_inicio
        dias_contados = 0
        while dias_contados < num_dias:
            fecha_actual -= timedelta(days=1)
            if self.es_dia_laboral(fecha_actual):
                dias_contados += 1
        return fecha_actual

    def obtener_siguiente_dia_laboral(self, fecha: date) -> date:
        fecha_actual = fecha + timedelta(days=1)
        while not self.es_dia_laboral(fecha_actual):
            fecha_actual += timedelta(days=1)
        return fecha_actual

    def esta_en_periodo_bloqueado_vacaciones(
        self, fecha: date, dias_antes: int = 15, dias_despues: int = 15
    ) -> Tuple[bool, str]:
        """Verifica si una fecha esta en periodo bloqueado alrededor de vacaciones."""
        for inicio_vac, fin_vac in self._vacaciones_cache:
            fecha_bloqueo_inicio = self.restar_dias_laborales(inicio_vac, dias_antes)
            fecha_bloqueo_fin = self.agregar_dias_laborales(fin_vac, dias_despues)

            if fecha_bloqueo_inicio <= fecha <= inicio_vac:
                return True, f"Bloqueado: {dias_antes} dias laborales antes de vacaciones ({inicio_vac})"
            if fin_vac <= fecha <= fecha_bloqueo_fin:
                return True, f"Bloqueado: {dias_despues} dias laborales despues de vacaciones ({fin_vac})"
        return False, ""

    def esta_cerca_de_festivo(self, fecha: date) -> Tuple[bool, str]:
        """Verifica si la fecha es 1 dia laboral antes o despues de un festivo."""
        festivos = self._cargar_festivos(fecha.year)
        for festivo in festivos:
            dia_antes = self.restar_dias_laborales(festivo, 1)
            dia_despues = self.agregar_dias_laborales(festivo, 1)
            if fecha == dia_antes:
                return True, f"Bloqueado: 1 dia laboral antes de festivo ({festivo})"
            if fecha == dia_despues:
                return True, f"Bloqueado: 1 dia laboral despues de festivo ({festivo})"
        return False, ""

    def obtener_festivos(self, anio: int) -> List[date]:
        return self._cargar_festivos(anio)

    def obtener_vacaciones(self) -> List[Tuple[date, date]]:
        return self._vacaciones_cache


calendario_service = CalendarioService()
