# Sistema de Gestion RH - SEP/CORDE Tehuacan

Sistema de auto-servicio para gestion de recursos humanos de la coordinacion SEP/CORDE Tehuacan, Puebla.

## Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| Backend | FastAPI (Python 3.10+) + SQLAlchemy + SQLite |
| Frontend | React 18 + Vite + TailwindCSS v4 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Deploy | Windows 10, red local, puerto 8080 |

## Estructura del Proyecto

```
RH/
├── backend/
│   ├── app/
│   │   ├── models/        # 10 modelos SQLAlchemy
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── routes/        # Endpoints API (auth, empleados, justificantes, prestaciones, documentos, adeudos, notificaciones)
│   │   ├── services/      # Logica de negocio (auth, calendario, notificaciones)
│   │   ├── validators/    # Validadores (dia economico, permisos horas, prestaciones, calendario)
│   │   ├── utils/         # Security, dependencies, helpers
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── data/              # SQLite DB, formatos PDF, documentos generados
│   ├── scripts/           # create_root_user.py, seed_test_data.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/    # Layout (Navbar, Sidebar), Common (ProtectedRoute)
│       ├── pages/         # Login, Dashboards (Empleado, RH, Root), modulos
│       ├── contexts/      # AuthContext, NotificationContext
│       └── services/      # api.js (axios)
├── docs/
├── CLAUDE.md
├── ESPECIFICACIONES_SISTEMA_RH_SEP.md
├── GUIA_INICIO_CLAUDE_CODE.md
├── CODIGO_INICIAL.md
└── README.md
```

## Instalacion

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python scripts/create_root_user.py
python scripts/seed_test_data.py
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usuarios de Prueba

| Rol | Usuario | Password |
|-----|---------|----------|
| ROOT | david | Admin123! |
| ADMIN | maria.lopez | Temp123! |
| ADMIN | ana.garcia | Temp123! |
| USUARIO | juan.perez | Temp123! |
| USUARIO | pedro.martinez | Temp123! |
| USUARIO | carlos.ramirez | Temp123! |

## Modulos

| Modulo | Estado | Descripcion |
|--------|--------|-------------|
| Autenticacion | Completo | Login JWT, roles (ROOT/ADMIN/USUARIO), cambio/reset password |
| Empleados | Completo | CRUD completo con contadores automaticos |
| Justificantes | Completo | Dias economicos, permisos horas, ISSTEP, comisiones + PDF generation (F/004) |
| Prestaciones | Completo | 7 tipos, validaciones, aprobar/rechazar, upload documentos |
| Documentos | Completo | Solicitudes bidireccionales empleado<->RH, upload archivos |
| Adeudos | Completo | Dias pendientes, justificantes faltantes, documentos pendientes. Marcar/resolver con notificaciones |
| Notificaciones | Completo | Polling cada 30s, marcar leidas, badge en navbar |
| Reportes | Completo | 8 reportes (ausentismo, dias economicos, permisos horas, prestaciones, justificantes, adeudos, extemporaneos, estadisticas) + export Excel |
| PDF Generation | Completo | Generacion PDF con reportlab: justificantes (F/004) y prestaciones (F/005) |
| Calendario Laboral | Completo | Festivos 2026, vacaciones, dias laborales, periodos bloqueados |
| Auditoria | Completo | Log de todas las acciones criticas |

## API Docs

Con el backend corriendo: http://localhost:8080/docs (Swagger UI automatico de FastAPI)

## Notas Tecnicas

- passlib requiere `bcrypt==4.0.1` (no compatible con bcrypt 5.x)
- TailwindCSS v4 usa `@import "tailwindcss"` + plugin `@tailwindcss/vite`
- Vite proxy configurado: `/api` -> `http://localhost:8080`
- Base de datos SQLite en `backend/data/empleados.db`
- `api.js` usa baseURL vacio `''` para funcionar via proxy Vite (no `http://localhost:8080`)
- Interceptor axios agrega trailing slash para evitar redirect 307 que pierde Authorization headers

## Despliegue smith-dev (VM)

- Acceso: SSH via Tailscale `100.118.252.111` (Kamrui/Proxmox) -> `smith@192.168.1.70`
- Port forwarding: iptables en Kamrui redirige puertos 5173 y 8080 de Tailscale a smith-dev
- URL: http://100.118.252.111:5173
