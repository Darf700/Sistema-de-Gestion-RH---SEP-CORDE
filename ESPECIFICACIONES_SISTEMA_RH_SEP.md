# Sistema de Gestión RH - SEP/CORDE Tehuacán

## Información del Proyecto

**Cliente:** SEP/CORDE Tehuacán, Puebla, México  
**Desarrollador:** David (Coordinador de Tecnología)  
**Usuarios:** 49 empleados + 4 administradoras RH + 1 root  
**Timeline:** 3.5 semanas  
**Deployment:** PC Windows 10 en oficina (red local)  
**Stack:** FastAPI (Python) + React + SQLite

---

## Contexto

Actualmente el llenado de formatos de justificantes y prestaciones es manual, propenso a errores, y consume mucho tiempo de RH. Se requiere un sistema de auto-servicio donde los empleados puedan generar sus propios documentos, con validaciones automáticas según las reglas oficiales de SEP.

---

## Objetivos del Sistema

1. **Auto-servicio para empleados:** Generar justificantes y solicitar prestaciones sin ir a RH
2. **Validaciones automáticas:** Evitar errores y solicitudes inválidas
3. **Gestión centralizada:** RH puede ver todo, gestionar adeudos, generar reportes
4. **Expediente digital:** Cada empleado tiene su historial y documentos
5. **Auditoría completa:** Log de quién generó qué y cuándo

---

## Usuarios y Roles

### 1. ROOT (1 usuario)
- **Usuario:** `david`
- **Permisos:** TOTALES - Todo el sistema
- **Funciones especiales:**
  - Gestión de usuarios (crear/editar/eliminar)
  - Asignar roles
  - Configuración del sistema
  - Acceso a logs técnicos
  - Backup/Restore
  - Configurar calendario laboral
  - Gestionar formatos PDF

### 2. ADMIN - RH (4 usuarios)
- **Usuarios:** Por nombre (ej: `maria.lopez`, `ana.martinez`)
- **Permisos:** Gestión RH completa
- **Funciones:**
  - Ver todos los empleados (49)
  - Ver todos los justificantes y prestaciones
  - Gestión de datos de empleados
  - Marcar/quitar adeudos
  - Enviar notificaciones
  - Generar reportes y estadísticas
  - Subir/actualizar formatos PDF
  - Resetear contraseñas de empleados
  - Ver auditoría completa

### 3. USUARIO - Empleado (49 usuarios)
- **Usuarios:** Por nombre (ej: `juan.perez`)
- **Permisos:** Solo sus propios datos
- **Funciones:**
  - Ver dashboard personal
  - Generar justificantes
  - Solicitar prestaciones
  - Ver historial personal
  - Descargar/imprimir PDFs
  - Ver contadores (días económicos, permisos)
  - Subir documentos solicitados
  - Ver notificaciones y adeudos

---

## Módulos del Sistema

### MÓDULO 1: AUTENTICACIÓN Y SEGURIDAD

**Características:**
- Login con usuario y contraseña
- Contraseñas hasheadas con bcrypt
- Sesiones JWT
- Timeout automático: 30 minutos de inactividad
- Recuperación de contraseña: Solo ROOT/ADMIN pueden resetear
- Cambio de contraseña obligatorio en primer login
- Validación de permisos en cada acción

**Auditoría:**
- Log de accesos (quién, cuándo, desde dónde)
- Log de acciones (qué hizo, timestamp)
- Historial de cambios en datos sensibles

---

### MÓDULO 2: JUSTIFICANTES

#### Tipos de Justificantes:

**1. Día Económico**
- Cada solicitud = **3 días LABORALES consecutivos**
- Máximo **3 solicitudes por año fiscal** (= 9 días totales)
- Año fiscal: 1 enero - 31 diciembre

**Reglas de Validación:**
- ✅ Mínimo **30 días LABORALES** entre cada solicitud
- ✅ **NO se puede solicitar** 15 días laborales antes/después de vacaciones
- ✅ **NO se puede solicitar** un día antes/después de días del calendario oficial
- ✅ **NO se puede iniciar en viernes** (deben ser 3 días laborales consecutivos)
- ✅ Días válidos para iniciar: Lunes, Martes, Miércoles
- ⏰ **Extemporáneo:** Si se entrega después del 3er día hábil

**Contador:**
```
- Solicitudes usadas en 2026: X/3
- Días económicos usados: X/9
- Última solicitud: [fecha]
- Próxima solicitud disponible: [fecha calculada]
```

**2. Permiso por Horas**
- Duración fija: **3 horas**
- Solo de **entrada O salida** (no entre medias)
- Máximo **2 permisos por quincena** = 4 al mes
- Debe registrar entrada Y salida en el sistema

**Quincenas:**
- Quincena 1: días 1-15 del mes
- Quincena 2: días 16-fin de mes

**3. ISSSTE(P)**
- Tiempo de traslado:
  - 1 hora máximo para unidad local
  - 1.5 horas para unidades foráneas
- Debe adjuntar comprobante de asistencia
- Debe registrar entrada/salida

**4. Comisiones**
- **Comisión Todo el Día**
- **Comisión Entrada**
- **Comisión Salida**
- Requiere:
  - Motivo
  - Lugar
  - Fecha(s)
  - Sellos del lugar comisionado (físicamente)

---

### MÓDULO 3: PRESTACIONES

#### Tipos de Prestaciones Activas:

**1. Licencias Médicas**
- Requiere dictamen médico del ISSSTE(P)
- Validación: 6 meses + 1 día de antigüedad

**2. Cuidados Maternos/Paternos**
- Duración: Hasta 7 días hábiles por año natural
- Para hijos de hasta 8 años 11 meses
- Requiere dictamen médico ISSSTE(P)
- Documentos: Acta nacimiento hijo, carnet ISSSTE(P)

**3. Cuidados Médicos Familiares**
- Personal Apoyo/Asistencia Básica: Máximo 12 días hábiles/año
- Personal Docente: Máximo 14 días hábiles/año
- Año calendario: 1 enero - 31 diciembre
- Para: Cónyuge, Padres, Hijos que dependan económicamente
- Requiere dictamen médico ISSSTE(P)

**4. Permiso por Fallecimiento de Familiar Primer Grado**
- Básica: Hasta 5 días hábiles
- Media Superior/Superior: Hasta 6 días hábiles
- Familiar: Hijos, Cónyuge, Padres, Hermanos
- Requiere: Acta de defunción

**5. Media Hora de Tolerancia**
- Para padres con hijos en: Lactantes, Maternal, Preescolar, Primaria
- Solo si diferencia de traslado > 10 minutos
- Solo si entrada escuela = entrada trabajo (8:00 AM)
- Suspendido en periodos vacacionales y receso escolar
- Requiere: Constancia de estudios, Acta nacimiento hijo, Boucher inscripción

**6. Licencia por Nupcias**
- Duración: 5 días hábiles con goce de sueldo
- Requiere: Acta de matrimonio

**7. Licencia por Paternidad**
- Duración: 6 días con goce de sueldo
- Por nacimiento o adopción de hijo(a)
- Requiere: Constancia de concubinato o alumbramiento, acta nacimiento/adopción

**Validaciones Generales para Prestaciones:**
- ❌ NO aplica si tiene nombramiento: Interino, Limitado, Gravidez, Prejubilatorio
- ❌ NO aplica si recibe pago por Honorarios
- ❌ NO aplica si está en Licencia sin Goce de Sueldo
- ✅ Requiere mínimo 6 meses + 1 día de antigüedad

---

### MÓDULO 4: DOCUMENTOS

**Solicitudes de Empleado a RH:**
- Constancia laboral
- Carta de recomendación
- Comprobante de percepciones
- Constancia de antigüedad
- Otros documentos oficiales

**Estados:** Pendiente → En proceso → Listo → Entregado

**Solicitudes de RH a Empleado:**
- Actualización de CURP
- Comprobante domicilio
- Acta nacimiento hijos
- Cartilla militar
- RFC actualizado
- Certificados/diplomas
- Etc.

**Flujo:**
```
RH solicita → Empleado recibe notificación → 
Empleado sube archivo → RH valida/rechaza
```

---

### MÓDULO 5: ADEUDOS

**RH puede marcar adeudos:**
- Justificantes no entregados
- Documentos pendientes
- Otros conceptos

**Notificación:**
- Empleado recibe alerta cuando tiene adeudos
- Seguimiento de estado
- Historial de adeudos

---

### MÓDULO 6: GESTIÓN DE EMPLEADOS (Solo RH/ROOT)

**Datos por Empleado:**
- Nombre completo
- Clave(s) presupuestal(es)
- Horario de trabajo
- Adscripción
- Número de asistencia
- Tipo: Docente / Apoyo y Asistencia
- Fecha de ingreso (para antigüedad)
- Datos de contacto
- Beneficiarios
- Contactos de emergencia

**Contadores Automáticos:**
- Días económicos usados / disponibles
- Permisos por horas usados en quincena actual
- Prestaciones usadas en año actual
- Historial completo de justificantes

---

### MÓDULO 7: REPORTES Y ESTADÍSTICAS (Solo RH/ROOT)

**Reportes Disponibles:**
- Ausentismo por empleado
- Días económicos disponibles (todos los empleados)
- Permisos por horas por quincena
- Prestaciones otorgadas
- Justificantes generados por período
- Empleados con adeudos
- Justificantes extemporáneos
- Estadísticas por tipo de justificante
- Exportar a Excel/PDF

---

## Calendario Laboral

### Tipo de Personal
**Personal Administrativo** (los 49 empleados)
- Siguen calendario oficial federal
- NO calendario escolar
- Trabajan cuando no hay clases

### Año Fiscal
- **Contador de días económicos:** 1 enero - 31 diciembre
- Resetea cada 1 de enero

### Días Laborales
**Se cuentan SOLO días laborales:**
- Lunes a Viernes
- Excluyendo sábados y domingos
- Excluyendo días festivos oficiales
- Excluyendo vacaciones administrativas

### Vacaciones Administrativas

**VERANO:**
- Duración: 15 días laborales (~3 semanas calendario)
- Escolares salen: 10 Julio 2026
- Administrativos salen: ~17 Julio 2026 (1 semana después)
- Escolares regresan: 25 Agosto 2026
- Administrativos regresan: ~18 Agosto 2026 (1 semana antes)
- **PENDIENTE:** Fechas exactas

**DICIEMBRE:**
- Duración: ~2 semanas
- Fechas aproximadas: 22 Dic 2025 - 6 Ene 2026
- **PENDIENTE:** Confirmación fechas exactas

**SEMANA SANTA:**
- Duración: 2 semanas
- Escolares: 6-17 Abril 2026
- Administrativos: **PENDIENTE** confirmación si mismas fechas

### Días Festivos Federales (NO laborables)

**2025:**
- 1 Enero - Año Nuevo
- 5 Febrero - Día de la Constitución (primer lunes)
- 17 Marzo - Natalicio de Benito Juárez (tercer lunes)
- 1 Mayo - Día del Trabajo
- 16 Septiembre - Independencia
- 18 Noviembre - Revolución (tercer lunes)
- 25 Diciembre - Navidad

**2026:**
- 1 Enero - Año Nuevo
- 2 Febrero - Día de la Constitución (primer lunes)
- 16 Marzo - Natalicio de Benito Juárez (tercer lunes)
- 1 Mayo - Día del Trabajo
- 16 Septiembre - Independencia
- 16 Noviembre - Revolución (tercer lunes)
- 25 Diciembre - Navidad

### Días Escolares (Administrativos SÍ trabajan)
- Consejos Técnicos Escolares
- Suspensión de labores docentes
- Períodos vacacionales escolares (excepto sus propias vacaciones)

### Validaciones de Calendario

**Para Días Económicos:**
- Bloquear 15 días laborales ANTES de inicio vacaciones
- Bloquear 15 días laborales DESPUÉS de fin vacaciones
- Bloquear 1 día laboral antes de festivo oficial
- Bloquear 1 día laboral después de festivo oficial

**Ejemplo de cálculo:**
```
Vacaciones verano: 17 Julio - 18 Agosto 2026
Período bloqueado:
- 15 días laborales antes del 17 Julio
- 15 días laborales después del 18 Agosto
```

---

## Generación de PDFs

### Formatos Disponibles
1. **Formato de Justificantes** (SEP-1.3.1.3/DRH/F/004 Ver. 15)
2. **Formato de Prestaciones** (SEP-1.3.1.3/DRH/F/005 Ver. 15)

### Características
- PDFs son **editables** (formularios con campos)
- Se llenan programáticamente con PyPDF2 o pdf-forms
- Sistema de carpeta: `/data/formatos/` para templates
- Generados se guardan en: `/data/generados/`

### Campos a Llenar Automáticamente

**Encabezado:**
- Fecha: "Cuatro veces Heroica Puebla de Zaragoza", a [día] de [mes] de [año]
- Para: [Área]
- Inmueble: [Inmueble]
- Nombre empleado
- Horario
- Clave(s) Presupuestal(es)
- Adscripción
- Número de asistencia

**Contenido según tipo:**
- Fechas calculadas
- Conceptos seleccionados (checkboxes)
- Motivos
- Horas específicas
- Períodos

**Firmas (físicas - NO digitales):**
- Vo.Bo. JEFE(A) INMEDIATO
- AUTORIZÓ TITULAR DEL ÁREA
- RECIBIDO

### Flujo de Generación
```
1. Usuario llena formulario web
2. Sistema valida datos
3. Sistema calcula fechas/períodos
4. Sistema llena PDF template
5. PDF generado se guarda con nombre único
6. Usuario puede descargar o imprimir
7. Usuario imprime, firma físicamente
8. Usuario entrega a RH
9. Sistema registra en auditoría
```

---

## Notificaciones

### Sistema de Notificaciones Interno

**Empleado recibe notificación cuando:**
- ✉️ RH solicita un documento
- ✉️ Tiene adeudos pendientes
- ✉️ Documento solicitado está listo
- ✉️ Próxima solicitud de día económico disponible (recordatorio)

**RH recibe notificación cuando:**
- ✉️ Nuevo justificante generado
- ✉️ Empleado subió documento solicitado
- ✉️ Nueva solicitud de documento
- ✉️ Empleado actualizó datos personales (pendiente aprobación)

**NO se implementa email** - Solo notificaciones en sistema

---

## Estructura de Base de Datos

### Tablas Principales

**users**
```sql
id, username, password_hash, role (ROOT/ADMIN/USUARIO), 
empleado_id (FK), created_at, last_login, 
password_changed, active
```

**empleados**
```sql
id, nombre_completo, claves_presupuestales, 
horario, adscripcion, numero_asistencia, 
tipo (Docente/Apoyo), fecha_ingreso, 
contacto_email, contacto_telefono, activo
```

**justificantes**
```sql
id, empleado_id, tipo, fecha_generacion, 
fecha_inicio, fecha_fin, dias_solicitados,
motivo, lugar (comisiones), horas_inicio, horas_fin,
pdf_path, estado (Generado/Entregado/Extemporáneo),
created_by_user_id, created_at
```

**prestaciones**
```sql
id, empleado_id, tipo, fecha_solicitud, 
fecha_inicio, fecha_fin, dias_solicitados,
documentos_adjuntos, estado (Pendiente/Aprobado/Rechazado),
aprobado_por_user_id, created_at
```

**documentos**
```sql
id, empleado_id, tipo, descripcion, 
solicitado_por (Empleado/RH), 
estado (Pendiente/EnProceso/Listo/Entregado),
archivo_path, fecha_solicitud, fecha_entrega
```

**adeudos**
```sql
id, empleado_id, tipo, descripcion, 
monto (opcional), estado (Pendiente/Pagado),
marcado_por_user_id, fecha_marcado, fecha_resuelto
```

**notificaciones**
```sql
id, usuario_id, tipo, mensaje, 
leida (bool), created_at
```

**contadores**
```sql
id, empleado_id, año, 
dias_economicos_usados, solicitudes_economicos,
permisos_horas_quincena_actual, fecha_ultima_solicitud_economico,
cuidados_medicos_usados, otras_prestaciones (JSON)
```

**calendario_laboral**
```sql
id, fecha, tipo (Festivo/Vacacion/Laboral),
descripcion, año
```

**audit_log**
```sql
id, user_id, accion, tabla_afectada, 
registro_id, datos_anteriores (JSON), 
datos_nuevos (JSON), ip_address, timestamp
```

---

## Stack Tecnológico

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **ORM:** SQLAlchemy
- **Base de datos:** SQLite (archivo local)
- **Autenticación:** JWT (python-jose)
- **Contraseñas:** bcrypt (passlib)
- **PDFs:** PyPDF2 o pypdf
- **Validaciones:** Pydantic
- **CORS:** Para permitir frontend

### Frontend
- **Framework:** React 18 + Vite
- **Styling:** TailwindCSS
- **Routing:** React Router v6
- **State Management:** Context API + hooks
- **HTTP Client:** Axios
- **Formularios:** React Hook Form
- **Datepicker:** React DatePicker
- **PDF Preview:** react-pdf
- **Notificaciones:** React Toastify
- **Iconos:** Lucide React o Hero Icons

### Infraestructura
- **OS:** Windows 10
- **Python:** Ya instalado
- **Servidor:** Uvicorn (incluido con FastAPI)
- **Puerto:** 8080 (configurable)
- **Red:** Local (no internet público)
- **Acceso:** http://[IP-PC-OFICINA]:8080

---

## Estructura del Proyecto

```
sistema-rh-sep/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── empleado.py
│   │   │   ├── justificante.py
│   │   │   ├── prestacion.py
│   │   │   ├── documento.py
│   │   │   ├── adeudo.py
│   │   │   ├── notificacion.py
│   │   │   ├── contador.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── empleado.py
│   │   │   ├── justificante.py
│   │   │   └── ... (uno por modelo)
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── empleados.py
│   │   │   ├── justificantes.py
│   │   │   ├── prestaciones.py
│   │   │   ├── documentos.py
│   │   │   ├── adeudos.py
│   │   │   ├── reportes.py
│   │   │   └── admin.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── justificante_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── validacion_service.py
│   │   │   ├── calendario_service.py
│   │   │   └── notificacion_service.py
│   │   │
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   ├── dia_economico_validator.py
│   │   │   ├── permiso_horas_validator.py
│   │   │   ├── prestacion_validator.py
│   │   │   └── calendario_validator.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py
│   │       ├── dependencies.py
│   │       └── helpers.py
│   │
│   ├── data/
│   │   ├── empleados.db
│   │   ├── formatos/
│   │   │   ├── justificantes_v15.pdf
│   │   │   └── prestaciones_v15.pdf
│   │   ├── generados/
│   │   │   └── (PDFs generados organizados por fecha)
│   │   └── documentos/
│   │       └── (uploads organizados por empleado)
│   │
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Input.jsx
│   │   │   │   ├── Select.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── Table.jsx
│   │   │   │   └── Notification.jsx
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Layout.jsx
│   │   │   │
│   │   │   ├── justificantes/
│   │   │   │   ├── FormularioJustificante.jsx
│   │   │   │   ├── ListaJustificantes.jsx
│   │   │   │   └── ValidacionDiaEconomico.jsx
│   │   │   │
│   │   │   ├── prestaciones/
│   │   │   ├── documentos/
│   │   │   └── admin/
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── DashboardEmpleado.jsx
│   │   │   ├── DashboardRH.jsx
│   │   │   ├── DashboardRoot.jsx
│   │   │   ├── Justificantes.jsx
│   │   │   ├── Prestaciones.jsx
│   │   │   ├── Documentos.jsx
│   │   │   ├── MiPerfil.jsx
│   │   │   └── Reportes.jsx
│   │   │
│   │   ├── contexts/
│   │   │   ├── AuthContext.jsx
│   │   │   └── NotificationContext.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   ├── justificanteService.js
│   │   │   └── empleadoService.js
│   │   │
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   ├── formatters.js
│   │   │   └── validators.js
│   │   │
│   │   └── styles/
│   │       └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── README.md
│
├── docs/
│   ├── MANUAL_USUARIO.md
│   ├── MANUAL_ADMIN.md
│   ├── INSTALACION.md
│   └── API_DOCS.md
│
└── README.md
```

---

## Instalación y Deployment

### Requisitos
- Windows 10
- Python 3.10+ (ya instalado)
- Node.js 18+ (para frontend)
- 4GB RAM mínimo
- 10GB espacio en disco

### Instalación Backend

```bash
# En carpeta del proyecto
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python init_db.py

# Crear usuario ROOT inicial
python create_root_user.py

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Instalación Frontend

```bash
# En carpeta frontend
cd frontend

# Instalar dependencias
npm install

# Configurar API endpoint (crear .env)
VITE_API_URL=http://localhost:8080

# Modo desarrollo
npm run dev

# Build para producción
npm run build

# Los archivos compilados estarán en dist/
```

### Deployment Producción

**Opción 1: Servidor local simple**
```bash
# Backend como servicio de Windows
# Usar NSSM o similar para registrar como servicio

# Frontend servido por backend
# Copiar dist/ a backend/static/
# FastAPI sirve archivos estáticos
```

**Opción 2: Nginx como reverse proxy**
```
# Instalar Nginx en Windows
# Configurar para servir frontend y proxy al backend
```

---

## Seguridad

### Contraseñas
- Hash con bcrypt (costo factor 12)
- Mínimo 8 caracteres
- Cambio obligatorio en primer login
- No reutilización de últimas 3 contraseñas

### Sesiones
- JWT con expiración
- Refresh tokens
- Timeout: 30 minutos inactividad
- Logout automático

### Permisos
- Verificación en cada endpoint
- Decoradores de autorización
- Validación de rol antes de acción

### Datos Sensibles
- No logs de contraseñas
- Sanitización de inputs
- Protección CSRF
- CORS configurado solo para red local

### Backups
- Backup automático diario de SQLite
- Carpeta: `/data/backups/`
- Retención: 30 días
- Backup manual disponible para ROOT

---

## Testing

### Backend
```bash
# Unit tests
pytest tests/

# Coverage
pytest --cov=app tests/
```

### Frontend
```bash
# Tests
npm test

# E2E con Playwright
npm run test:e2e
```

### Tests Críticos
- ✅ Validación días económicos
- ✅ Cálculo de días laborales
- ✅ Validación períodos vacacionales
- ✅ Contadores de permisos por quincena
- ✅ Generación de PDFs
- ✅ Autenticación y permisos
- ✅ Auditoría de acciones

---

## Datos Pendientes

### Información que se necesita proporcionar:

1. **Fechas exactas vacaciones administrativas 2025-2026:**
   - Verano: Último día laboral / Primer día de regreso
   - Diciembre: Fechas exactas
   - Semana Santa: Confirmación fechas

2. **Lista de empleados (puede ser parcial para iniciar):**
   - Nombre completo
   - Clave(s) presupuestal(es)
   - Horario
   - Adscripción
   - Número de asistencia
   - Tipo (Docente/Apoyo)
   - Fecha de ingreso

3. **Nombres de las 4 jefas RH:**
   - Para crear usuarios ADMIN

4. **Logo SEP (opcional):**
   - Para interfaz
   - Formato PNG o SVG

5. **Nombre del inmueble:**
   - Aparece en formatos PDF

---

## Timeline Detallado

### Semana 1: Core + Autenticación (5 días)

**Día 1-2: Setup y Base de Datos**
- Estructura del proyecto
- Configuración FastAPI
- Modelos SQLAlchemy
- Migraciones iniciales
- Seeders con datos de prueba

**Día 3-4: Autenticación y Roles**
- Sistema de login
- JWT tokens
- Middleware de autenticación
- Decoradores de autorización
- CRUD usuarios
- Gestión de roles

**Día 5: Módulo Empleados**
- CRUD empleados
- Frontend básico de login
- Dashboard esqueleto por rol
- Contexto de autenticación React

### Semana 2: Justificantes (5 días)

**Día 1-2: Generador de Justificantes**
- API endpoints justificantes
- Formularios frontend
- Validaciones básicas
- Guardado en BD

**Día 3-4: Validaciones Complejas**
- Calendario laboral service
- Validador días económicos
- Validador permisos por horas
- Contadores automáticos
- Tests de validaciones

**Día 5: Generación PDFs**
- Integración PyPDF2
- Llenado de formularios PDF
- Preview en frontend
- Descarga/impresión

### Semana 3: Prestaciones + Documentos (5 días)

**Día 1-2: Módulo Prestaciones**
- API prestaciones
- Formularios por tipo
- Validaciones específicas
- Upload de documentos adjuntos
- Contadores por prestación

**Día 3-4: Módulo Documentos y Adeudos**
- Solicitudes empleado → RH
- Solicitudes RH → empleado
- Upload de archivos
- Gestión de adeudos
- Sistema de notificaciones

**Día 5: Notificaciones**
- Centro de notificaciones
- Notificaciones en tiempo real (polling)
- Marcado de leídas
- Alertas visuales

### Semana 3.5: Admin, Reportes y Deploy (3.5 días)

**Día 1-2: Dashboard RH y Reportes**
- Vista general empleados
- Reportes y estadísticas
- Filtros y búsquedas
- Exportar a Excel/PDF
- Gestión de formatos PDF

**Día 3: Testing Completo**
- Tests unitarios críticos
- Tests de integración
- Tests E2E de flujos principales
- Corrección de bugs

**Medio Día 4: Deploy y Documentación**
- Manual de usuario
- Manual de administrador
- Instalación en PC oficina
- Configuración de red local
- Capacitación básica a jefas RH

---

## Consideraciones Especiales

### Calendario Laboral
- El sistema debe recalcular días laborales excluyendo correctamente:
  - Fines de semana
  - Festivos oficiales
  - Vacaciones administrativas
- Función helper: `calcular_dias_laborales(fecha_inicio, fecha_fin)`
- Función helper: `agregar_dias_laborales(fecha_inicio, num_dias)`

### Quincenas
- Quincena actual se calcula por fecha del sistema
- Contador de permisos por horas se resetea cada quincena
- Validación: "¿Estamos en quincena 1 o 2?"

### Años
- Días económicos: Año fiscal (enero-diciembre)
- Prestaciones: Algunos por año calendario, otros por año escolar
- Sistema debe manejar múltiples contadores

### Extemporáneos
- Justificante se marca extemporáneo si se entrega después del 3er día hábil
- Cálculo: contar días HÁBILES desde fecha del evento
- Alerta visual en sistema

### Auditoría
- Cada acción crítica se registra
- Formato: `{usuario} {acción} {recurso} el {timestamp}`
- Ejemplos:
  - "juan.perez generó justificante día económico el 2026-02-15 10:30"
  - "maria.lopez marcó adeudo a pedro.garcia el 2026-02-15 11:45"

---

## API Endpoints Principales

### Autenticación
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/change-password` - Cambiar contraseña
- `POST /api/auth/reset-password` - Resetear contraseña (ADMIN/ROOT)

### Empleados
- `GET /api/empleados` - Listar (filtros, paginación)
- `GET /api/empleados/{id}` - Ver detalle
- `POST /api/empleados` - Crear (ROOT/ADMIN)
- `PUT /api/empleados/{id}` - Actualizar (ROOT/ADMIN)
- `DELETE /api/empleados/{id}` - Eliminar (ROOT)
- `GET /api/empleados/{id}/contadores` - Ver contadores

### Justificantes
- `GET /api/justificantes` - Listar (usuario ve solo suyos)
- `GET /api/justificantes/{id}` - Ver detalle
- `POST /api/justificantes` - Crear
- `POST /api/justificantes/validar` - Validar antes de crear
- `GET /api/justificantes/{id}/pdf` - Descargar PDF
- `GET /api/justificantes/tipos` - Listar tipos disponibles

### Prestaciones
- `GET /api/prestaciones` - Listar
- `GET /api/prestaciones/{id}` - Ver detalle
- `POST /api/prestaciones` - Solicitar
- `PUT /api/prestaciones/{id}/aprobar` - Aprobar (ADMIN)
- `PUT /api/prestaciones/{id}/rechazar` - Rechazar (ADMIN)
- `GET /api/prestaciones/catalogo` - Catálogo con requisitos

### Documentos
- `GET /api/documentos` - Listar
- `POST /api/documentos/solicitar-a-rh` - Empleado solicita
- `POST /api/documentos/solicitar-a-empleado` - RH solicita (ADMIN)
- `POST /api/documentos/{id}/upload` - Subir archivo
- `PUT /api/documentos/{id}/estado` - Cambiar estado

### Adeudos
- `GET /api/adeudos` - Listar
- `POST /api/adeudos` - Marcar adeudo (ADMIN)
- `PUT /api/adeudos/{id}` - Actualizar estado
- `DELETE /api/adeudos/{id}` - Quitar adeudo (ADMIN)

### Notificaciones
- `GET /api/notificaciones` - Mis notificaciones
- `PUT /api/notificaciones/{id}/leer` - Marcar como leída
- `PUT /api/notificaciones/leer-todas` - Marcar todas

### Reportes (ADMIN/ROOT)
- `GET /api/reportes/ausentismo` - Por empleado/período
- `GET /api/reportes/dias-economicos` - Disponibles/usados
- `GET /api/reportes/prestaciones` - Por tipo/período
- `GET /api/reportes/export` - Exportar (Excel/PDF)

### Admin (ROOT)
- `GET /api/admin/usuarios` - Listar usuarios
- `POST /api/admin/usuarios` - Crear usuario
- `PUT /api/admin/usuarios/{id}` - Editar usuario
- `DELETE /api/admin/usuarios/{id}` - Eliminar
- `POST /api/admin/formatos/upload` - Subir formato PDF
- `GET /api/admin/audit-log` - Ver logs de auditoría
- `POST /api/admin/backup` - Crear backup manual

### Utilidades
- `GET /api/calendario/dias-laborales` - Calcular días laborales
- `GET /api/calendario/festivos/{año}` - Listar festivos
- `GET /api/calendario/vacaciones/{año}` - Períodos vacacionales

---

## Notas Finales

### Prioridades
1. **Funcionalidad sobre diseño** - Que funcione correctamente primero
2. **Validaciones precisas** - Evitar errores de reglas de negocio
3. **Auditoría completa** - Trazabilidad de todas las acciones
4. **Interfaz clara** - Que cualquiera pueda usar sin capacitación extensa

### Escalabilidad Futura
- El sistema está diseñado para 49 empleados
- SQLite es suficiente para este volumen
- Si crece, migración a PostgreSQL es directa (mismo SQLAlchemy)
- Arquitectura permite agregar módulos sin afectar existentes

### Mantenimiento
- Formatos PDF en carpeta, fácil de actualizar
- Calendario laboral configurable
- Reglas de validación centralizadas
- Código documentado

### Capacitación
- Manual de usuario (empleados)
- Manual de administrador (RH)
- Video tutorial corto para cada rol
- Datos de prueba para practicar

---

## Contacto y Soporte

**Desarrollador:** David  
**Rol:** Coordinador de Tecnología SEP/CORDE  
**Ubicación:** Tehuacán, Puebla, México

**Para Claude Code:**
Este documento contiene todas las especificaciones necesarias para desarrollar el sistema completo. Cualquier duda sobre reglas de negocio, validaciones o funcionalidades específicas puede consultarse directamente en este documento.

---

*Documento generado: Febrero 2026*  
*Versión: 1.0*  
*Proyecto: Sistema de Gestión RH - SEP/CORDE Tehuacán*
