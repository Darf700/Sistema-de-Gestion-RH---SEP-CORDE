# Guía de Inicio - Sistema RH SEP/CORDE para Claude Code

## Contexto Rápido

Estás construyendo un sistema de gestión de RH para una oficina gubernamental (SEP/CORDE) en México con 49 empleados. El sistema automatiza la generación de justificantes y gestión de prestaciones que actualmente se hacen manualmente.

**Timeline:** 3.5 semanas  
**Deploy:** PC Windows 10 en red local  
**Usuario principal:** David (desarrollador y coordinador de tecnología)

---

## Documento Principal

Lee primero: `ESPECIFICACIONES_SISTEMA_RH_SEP.md`

Ese documento contiene TODAS las especificaciones completas del proyecto.

---

## Orden de Desarrollo Sugerido

### FASE 1: Setup y Autenticación (Semana 1)

#### Paso 1.1: Estructura del Proyecto
```bash
# Crear estructura base
mkdir sistema-rh-sep
cd sistema-rh-sep
mkdir -p backend/app/{models,schemas,routes,services,validators,utils}
mkdir -p backend/data/{formatos,generados,documentos}
mkdir -p frontend/src/{components,pages,contexts,services,utils}
mkdir docs
```

#### Paso 1.2: Backend Base
**Archivos a crear:**
1. `backend/requirements.txt` - Dependencias Python
2. `backend/app/config.py` - Configuración (DB, JWT, etc)
3. `backend/app/database.py` - SQLAlchemy setup
4. `backend/app/main.py` - FastAPI app principal

**Dependencias principales:**
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pypdf
python-dateutil
```

#### Paso 1.3: Modelos de Base de Datos
**Orden de creación:**
1. `models/user.py` - Usuario (auth)
2. `models/empleado.py` - Empleado
3. `models/justificante.py` - Justificantes
4. `models/prestacion.py` - Prestaciones
5. `models/documento.py` - Documentos
6. `models/adeudo.py` - Adeudos
7. `models/notificacion.py` - Notificaciones
8. `models/contador.py` - Contadores
9. `models/audit_log.py` - Auditoría

#### Paso 1.4: Sistema de Autenticación
**Archivos críticos:**
- `utils/security.py` - Hash passwords, JWT tokens
- `routes/auth.py` - Login, logout, refresh
- `services/auth_service.py` - Lógica de autenticación

**Roles a implementar:**
- ROOT (permisos totales)
- ADMIN (gestión RH)
- USUARIO (empleado normal)

#### Paso 1.5: Frontend Base
**Setup React + Vite:**
```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install react-router-dom axios tailwindcss
npm install react-hook-form react-datepicker lucide-react
```

**Componentes iniciales:**
1. Login page
2. AuthContext (manejo de sesión)
3. Layout básico (Navbar, Sidebar)
4. Rutas protegidas por rol

---

### FASE 2: Módulo Justificantes (Semana 2)

#### Paso 2.1: Servicio de Calendario Laboral
**Archivo crítico:** `services/calendario_service.py`

**Funciones esenciales:**
```python
def es_dia_laboral(fecha: date) -> bool:
    """Verifica si una fecha es día laboral (no finde, no festivo, no vacaciones)"""
    
def calcular_dias_laborales(fecha_inicio: date, fecha_fin: date) -> int:
    """Cuenta días laborales entre dos fechas"""
    
def agregar_dias_laborales(fecha_inicio: date, num_dias: int) -> date:
    """Suma N días laborales a una fecha"""
    
def obtener_festivos(año: int) -> List[date]:
    """Retorna lista de festivos del año"""
    
def obtener_vacaciones(año: int) -> List[Tuple[date, date]]:
    """Retorna períodos de vacaciones administrativas"""
```

#### Paso 2.2: Validadores de Justificantes
**Archivos:**
- `validators/dia_economico_validator.py`
- `validators/permiso_horas_validator.py`

**Validaciones Día Económico:**
```python
class DiaEconomicoValidator:
    def validar_disponibilidad(empleado_id, fecha_inicio):
        """
        - Verifica que no haya usado 3 solicitudes en el año
        - Verifica 30 días laborales desde última solicitud
        - Verifica que no esté en período bloqueado (vacaciones ±15 días)
        - Verifica que no sea día antes/después de festivo
        - Verifica que inicie en lun/mar/mié (no viernes)
        """
```

**Validaciones Permiso por Horas:**
```python
class PermisoHorasValidator:
    def validar_quincena(empleado_id, fecha):
        """
        - Verifica que no haya usado 2 permisos en la quincena actual
        - Verifica que sean exactamente 3 horas
        - Verifica que sea de entrada O salida (no entre medias)
        """
```

#### Paso 2.3: API de Justificantes
**Endpoints:**
```python
# routes/justificantes.py

POST /api/justificantes/validar
    - Valida ANTES de crear
    - Retorna errores específicos o confirmación
    
POST /api/justificantes
    - Crea justificante
    - Actualiza contadores
    - Genera PDF
    - Registra en audit_log
    
GET /api/justificantes
    - Lista justificantes
    - Usuario: solo los suyos
    - Admin: todos con filtros
    
GET /api/justificantes/{id}/pdf
    - Descarga PDF generado
```

#### Paso 2.4: Generación de PDFs
**Archivo:** `services/pdf_service.py`

**Funcionalidad:**
```python
def llenar_formato_justificante(datos: dict) -> str:
    """
    1. Carga template PDF de /data/formatos/
    2. Llena campos según tipo de justificante
    3. Guarda en /data/generados/ con nombre único
    4. Retorna path del archivo generado
    """
```

**Campos a llenar:**
- Fecha completa en texto
- Nombre empleado
- Clave presupuestal
- Horario, adscripción, número asistencia
- Checkboxes según tipo
- Fechas calculadas
- Motivos, lugares

#### Paso 2.5: Frontend Justificantes
**Componentes:**
- `FormularioJustificante.jsx` - Formulario inteligente
- `SelectorFechas.jsx` - Con validaciones visuales
- `PreviewJustificante.jsx` - Muestra resumen antes de generar
- `ListaJustificantes.jsx` - Historial

**Flujo UX:**
```
1. Usuario selecciona tipo de justificante
2. Formulario se adapta al tipo
3. Usuario llena datos
4. Sistema valida en tiempo real (muestra alertas)
5. Preview del PDF
6. Confirmación → Genera y descarga
```

---

### FASE 3: Prestaciones y Documentos (Semana 3)

#### Paso 3.1: Módulo Prestaciones
Similar a justificantes pero con:
- Validaciones específicas por tipo de prestación
- Checklist de documentos requeridos
- Upload de archivos adjuntos
- Estados: Pendiente/Aprobado/Rechazado (si implementamos aprobación)

#### Paso 3.2: Módulo Documentos
- Solicitudes bidireccionales (empleado→RH y RH→empleado)
- Upload de archivos
- Estados de seguimiento
- Notificaciones

#### Paso 3.3: Sistema de Notificaciones
**Archivo:** `services/notificacion_service.py`

**Tipos de notificaciones:**
- Adeudos marcados
- Documentos solicitados
- Documentos listos
- Recordatorios

**Frontend:**
- Badge en navbar con contador
- Centro de notificaciones
- Marcar como leídas

---

### FASE 4: Admin y Reportes (Semana 3.5)

#### Paso 4.1: Dashboard RH
- Vista general de empleados
- Contadores agregados
- Alertas de extemporáneos
- Adeudos pendientes

#### Paso 4.2: Reportes
**Generación:**
- Filtros por fecha, empleado, tipo
- Export a Excel/PDF
- Gráficas básicas (opcional)

#### Paso 4.3: Gestión de Formatos
- Upload de nuevos PDFs
- Versionamiento básico
- Carpeta monitoreada

---

## Reglas de Negocio Críticas

### Día Económico
```
✓ 3 días LABORALES consecutivos
✓ Máximo 3 solicitudes/año (fiscal)
✓ 30 días LABORALES entre solicitudes
✓ NO 15 días laborales antes/después vacaciones
✓ NO 1 día laboral antes/después festivo oficial
✓ Solo puede iniciar: Lun/Mar/Mié (NO viernes)
```

### Permiso por Horas
```
✓ Exactamente 3 horas
✓ Solo entrada O salida
✓ Máximo 2 por quincena (quincena 1: días 1-15, quincena 2: días 16-fin)
```

### Prestaciones
```
✓ Antigüedad mínima: 6 meses + 1 día
✓ NO aplica si: Interino/Limitado/Gravidez/Prejubilatorio
✓ NO aplica si pago por Honorarios
✓ NO aplica si en Licencia sin Goce
```

### Calendario
```
Días laborales = Lunes a Viernes
                 - Festivos oficiales
                 - Vacaciones administrativas
                 
Festivos 2026:
  1 Ene, 2 Feb, 16 Mar, 1 May, 16 Sep, 16 Nov, 25 Dic
  
Vacaciones: PENDIENTE fechas exactas
```

---

## Datos de Prueba

### Usuarios Iniciales
```python
# ROOT
username: "david"
password: "Admin123!"
role: "ROOT"

# ADMIN (crear 4)
username: "rh.jefa1"
password: "Temp123!"
role: "ADMIN"

# USUARIOS (crear 5-10 para testing)
username: "juan.perez"
password: "Temp123!"
role: "USUARIO"
empleado_id: 1
```

### Empleados de Prueba
```python
{
    "nombre_completo": "Juan Pérez García",
    "claves_presupuestales": "E3618.001234",
    "horario": "08:00-15:00",
    "adscripcion": "Coordinación Tecnológica",
    "numero_asistencia": "001",
    "tipo": "Apoyo",
    "fecha_ingreso": "2020-01-15"
}
```

### Calendario de Prueba
```python
# Festivos 2026
festivos = [
    date(2026, 1, 1),   # Año Nuevo
    date(2026, 2, 2),   # Constitución
    date(2026, 3, 16),  # Benito Juárez
    date(2026, 5, 1),   # Trabajo
    date(2026, 9, 16),  # Independencia
    date(2026, 11, 16), # Revolución
    date(2026, 12, 25)  # Navidad
]

# Vacaciones (PLACEHOLDER - reemplazar con fechas reales)
vacaciones = [
    (date(2026, 7, 17), date(2026, 8, 18)),  # Verano
    (date(2025, 12, 22), date(2026, 1, 6)),  # Invierno
    (date(2026, 4, 6), date(2026, 4, 17))    # Semana Santa
]
```

---

## Testing Crítico

### Tests que DEBEN pasar antes de deploy:

**Validaciones:**
```python
def test_dia_economico_30_dias():
    # Verificar que no permite solicitud antes de 30 días laborales
    
def test_dia_economico_bloqueo_vacaciones():
    # Verificar bloqueo de 15 días antes/después vacaciones
    
def test_permiso_horas_quincena():
    # Verificar límite de 2 por quincena
    
def test_calcular_dias_laborales():
    # Verificar cálculo correcto excluyendo fines/festivos
```

**Generación PDFs:**
```python
def test_generar_pdf_dia_economico():
    # Verificar que genera PDF válido con datos correctos
    
def test_llenar_campos_pdf():
    # Verificar que todos los campos se llenan
```

**Autenticación:**
```python
def test_login_correcto():
def test_roles_permisos():
def test_timeout_sesion():
```

---

## Archivos de Configuración

### backend/app/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/empleados.db"
    
    # Security
    SECRET_KEY: str = "tu-secreto-super-seguro-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://192.168.x.x:8080"]
    
    # Paths
    FORMATOS_DIR: str = "./data/formatos"
    GENERADOS_DIR: str = "./data/generados"
    DOCUMENTOS_DIR: str = "./data/documentos"
    
    # Calendar (PLACEHOLDER - actualizar con fechas reales)
    VACACIONES_2026: list = [
        ("2026-07-17", "2026-08-18"),  # Verano
        ("2025-12-22", "2026-01-06"),  # Invierno
        ("2026-04-06", "2026-04-17")   # Semana Santa
    ]
    
    class Config:
        env_file = ".env"
```

### frontend/.env
```
VITE_API_URL=http://localhost:8080
```

---

## Comandos Útiles

### Backend
```bash
# Activar entorno virtual
cd backend
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Crear BD y tablas
python -c "from app.database import create_tables; create_tables()"

# Crear usuario ROOT inicial
python scripts/create_root_user.py

# Iniciar servidor desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Tests
pytest tests/ -v
```

### Frontend
```bash
cd frontend

# Instalar
npm install

# Desarrollo
npm run dev

# Build
npm run build

# Preview build
npm run preview
```

---

## Notas Importantes para Claude Code

### 1. Validaciones Son Críticas
Las reglas de días económicos y permisos son ESTRICTAS. El sistema debe prevenir errores, no solo reportarlos. Usa validaciones tanto en frontend (UX) como backend (seguridad).

### 2. Calendario Laboral es la Base
Todo gira alrededor de días LABORALES. La función `calcular_dias_laborales()` debe ser perfecta porque se usa en todas las validaciones.

### 3. Auditoría No es Opcional
Cada acción debe registrarse. RH necesita saber quién generó qué y cuándo.

### 4. PDFs Son la Salida Final
El sistema genera PDFs que se imprimen y firman físicamente. Los PDFs deben ser perfectos y profesionales.

### 5. Datos Pendientes
Hay información que se proporcionará después (fechas exactas vacaciones, lista empleados completa). Usa datos de prueba realistas mientras tanto.

### 6. Simplicidad > Complejidad
Este es un sistema interno para 49 personas. Prioriza que funcione bien sobre features avanzadas. No necesitas microservicios ni arquitecturas complejas.

### 7. Windows 10 Target
Considera que el deploy es Windows. Paths con `\` vs `/`, servicios de Windows, etc.

---

## Próximos Pasos

1. **Leer especificaciones completas:** `ESPECIFICACIONES_SISTEMA_RH_SEP.md`
2. **Crear estructura base del proyecto**
3. **Empezar con backend: DB + Auth**
4. **Implementar calendario laboral**
5. **Construir módulo justificantes con validaciones**
6. **Frontend básico para probar**
7. **Iterar según feedback**

---

## Contacto

Si tienes dudas sobre reglas de negocio o necesitas aclaraciones, todo está documentado en `ESPECIFICACIONES_SISTEMA_RH_SEP.md`. Si algo no está claro, pregunta antes de asumir.

**Desarrollador:** David  
**Proyecto:** Sistema RH SEP/CORDE  
**Inicio:** Febrero 2026  
**Deadline:** 3.5 semanas desde inicio

---

¡Éxito con el desarrollo! 🚀
