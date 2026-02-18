from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import create_tables
from .routes import adeudos, auth, documentos, empleados, justificantes, notificaciones, prestaciones, reportes

# Crear tablas al iniciar
create_tables()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(empleados.router, prefix="/api/empleados", tags=["empleados"])
app.include_router(justificantes.router, prefix="/api/justificantes", tags=["justificantes"])
app.include_router(prestaciones.router, prefix="/api/prestaciones", tags=["prestaciones"])
app.include_router(documentos.router, prefix="/api/documentos", tags=["documentos"])
app.include_router(adeudos.router, prefix="/api/adeudos", tags=["adeudos"])
app.include_router(notificaciones.router, prefix="/api/notificaciones", tags=["notificaciones"])
app.include_router(reportes.router, prefix="/api/reportes", tags=["reportes"])


@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
