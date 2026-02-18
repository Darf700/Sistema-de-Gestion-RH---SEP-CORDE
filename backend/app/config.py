from pydantic_settings import BaseSettings
from typing import List, Tuple


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sistema RH SEP/CORDE"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./data/empleados.db"

    # Security
    SECRET_KEY: str = "cambiar-en-produccion-usar-secreto-seguro-123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Paths
    FORMATOS_DIR: str = "./data/formatos"
    GENERADOS_DIR: str = "./data/generados"
    DOCUMENTOS_DIR: str = "./data/documentos"
    BACKUPS_DIR: str = "./data/backups"

    # Dias Economicos
    DIAS_ECONOMICOS_MAX_SOLICITUDES: int = 3
    DIAS_ECONOMICOS_DIAS_POR_SOLICITUD: int = 3
    DIAS_ECONOMICOS_SEPARACION_DIAS: int = 30
    DIAS_ECONOMICOS_BLOQUEO_VACACIONES: int = 15

    # Permisos por Horas
    PERMISOS_HORAS_DURACION: int = 3
    PERMISOS_HORAS_MAX_POR_QUINCENA: int = 2

    # Festivos 2026
    FESTIVOS_2026: List[Tuple[int, int]] = [
        (1, 1),    # Ano Nuevo
        (2, 2),    # Constitucion
        (3, 16),   # Benito Juarez
        (5, 1),    # Dia del Trabajo
        (9, 16),   # Independencia
        (11, 16),  # Revolucion
        (12, 25),  # Navidad
    ]

    # PDF
    PDF_INMUEBLE: str = "CORDE TEHUACAN"
    PDF_INSTITUCION: str = "SEP del Estado de Puebla"
    PDF_COORDINACION: str = "Coordinacion Regional de Desarrollo Educativo Tehuacan"
    PDF_DIR: str = "./data/pdfs"

    # Vacaciones Administrativas 2025-2026 (PLACEHOLDER - actualizar con fechas reales)
    VACACIONES_2026: List[Tuple[str, str]] = [
        ("2026-07-17", "2026-08-18"),  # Verano
        ("2025-12-22", "2026-01-06"),  # Invierno
        ("2026-04-06", "2026-04-17"),  # Semana Santa
    ]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
