# Reporte de Sesion - 2026-02-16

## Objetivo
Rediseno del modulo de Adeudos: cambiar de "deudas monetarias" (monto) a "dias pendientes y justificantes faltantes" (dias_debe).

## Cambios realizados

### Backend (5 archivos)

#### 1. `backend/app/models/adeudo.py`
- Eliminado campo `monto = Column(Float)`
- Agregado `dias_debe = Column(Integer, default=0)` - dias que debe el empleado
- Agregado `justificante_id = Column(Integer, ForeignKey("justificantes.id"), nullable=True)` - vinculo opcional al justificante faltante
- Agregado enum `TipoAdeudo`: `DIAS_PENDIENTES`, `JUSTIFICANTE_NO_ENTREGADO`, `DOCUMENTO_PENDIENTE`
- Eliminado import de `Float` de SQLAlchemy

#### 2. `backend/app/schemas/adeudo.py`
- `AdeudoCreate`: `monto` -> `dias_debe: int = 0`, agregado `justificante_id: Optional[int] = None`
- `AdeudoUpdate`: `monto` -> `dias_debe: Optional[int] = None`
- `AdeudoResponse`: `monto` -> `dias_debe: int = 0`, agregado `justificante_id`

#### 3. `backend/app/schemas/reporte.py`
- `AdeudoReporteItem`: `monto` -> `dias_debe`, agregado `justificante_id`
- `ReporteAdeudosResponse`: `monto_total_pendiente: float` -> `total_dias_pendientes: int`

#### 4. `backend/app/routes/adeudos.py`
- Creacion de adeudo usa `dias_debe` y `justificante_id` en lugar de `monto`
- Actualizacion usa `dias_debe` en lugar de `monto`
- Notificacion al empleado incluye cantidad de dias

#### 5. `backend/app/routes/reportes.py`
- `reporte_adeudos()`: suma `dias_debe` en lugar de `monto`
- `EXPORT_CONFIGS["adeudos"]`: columna "Dias" en lugar de "Monto", campo `dias_debe`

### Frontend (2 archivos)

#### 6. `frontend/src/pages/Adeudos.jsx`
- Formulario: campo "Dias que debe" (input number, min=0) reemplaza "Monto"
- Select de tipos actualizado: "Dias pendientes", "Justificante no entregado", "Documento pendiente" (sin "Otro")
- Tabla: columna "Dias" muestra `dias_debe` en lugar de "Monto" con formato `$`
- Estado del form: `dias_debe` reemplaza `monto`

#### 7. `frontend/src/pages/Reportes.jsx`
- Tab Adeudos - tarjeta resumen: "Total Dias Pendientes" en lugar de "Monto Pendiente"
- Tab Adeudos - tabla: columna "Dias" con `dias_debe` en lugar de "Monto" con formato `$`

## Verificacion
- DB eliminada y recreada con nuevo schema
- Seed ejecutado exitosamente (5 empleados, 6 usuarios)
- Endpoint POST /api/adeudos: crea adeudo con `dias_debe: 2` correctamente
- Endpoint GET /api/reportes/adeudos: retorna `total_dias_pendientes: 2` correctamente
- No quedan referencias a `monto` en ningun archivo del proyecto
- Frontend verificado funcionando en localhost:5173

## Notas
- La migracion se resolvio eliminando la DB y re-seeding (entorno dev)
- El enum `TipoAdeudo` se agrego al modelo pero las rutas siguen usando `tipo: str` para flexibilidad
- El campo `justificante_id` es nullable y opcional, permite vincular un adeudo a un justificante especifico
