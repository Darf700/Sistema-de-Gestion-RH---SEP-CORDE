# Código de Inicio - Sistema RH SEP/CORDE

Este archivo contiene snippets de código inicial para arrancar el desarrollo más rápidamente.

---

## Backend - Estructura Base

### 1. requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pypdf==4.0.1
python-dateutil==2.8.2
alembic==1.13.1
pytest==7.4.4
```

### 2. app/config.py
```python
from pydantic_settings import BaseSettings
from typing import List, Tuple
from datetime import date

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
        "http://127.0.0.1:5173"
    ]
    
    # Paths
    FORMATOS_DIR: str = "./data/formatos"
    GENERADOS_DIR: str = "./data/generados"
    DOCUMENTOS_DIR: str = "./data/documentos"
    BACKUPS_DIR: str = "./data/backups"
    
    # Días Económicos
    DIAS_ECONOMICOS_MAX_SOLICITUDES: int = 3
    DIAS_ECONOMICOS_DIAS_POR_SOLICITUD: int = 3
    DIAS_ECONOMICOS_SEPARACION_DIAS: int = 30
    DIAS_ECONOMICOS_BLOQUEO_VACACIONES: int = 15
    
    # Permisos por Horas
    PERMISOS_HORAS_DURACION: int = 3
    PERMISOS_HORAS_MAX_POR_QUINCENA: int = 2
    
    # Festivos 2026
    FESTIVOS_2026: List[Tuple[int, int]] = [
        (1, 1),    # Año Nuevo
        (2, 2),    # Constitución
        (3, 16),   # Benito Juárez
        (5, 1),    # Día del Trabajo
        (9, 16),   # Independencia
        (11, 16),  # Revolución
        (12, 25),  # Navidad
    ]
    
    # Vacaciones Administrativas 2025-2026 (PLACEHOLDER)
    # ACTUALIZAR con fechas exactas cuando se tengan
    VACACIONES_2026: List[Tuple[str, str]] = [
        ("2026-07-17", "2026-08-18"),  # Verano (PENDIENTE)
        ("2025-12-22", "2026-01-06"),  # Invierno (PENDIENTE)
        ("2026-04-06", "2026-04-17"),  # Semana Santa (PENDIENTE)
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3. app/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Eliminar todas las tablas (solo para desarrollo)"""
    Base.metadata.drop_all(bind=engine)
```

### 4. app/models/user.py
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class UserRole(str, enum.Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    empleado_id = Column(Integer, nullable=True)  # FK a empleados (null para ROOT/ADMIN sin empleado)
    
    active = Column(Boolean, default=True)
    password_changed = Column(Boolean, default=False)  # True después de primer cambio
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
```

### 5. app/models/empleado.py
```python
from sqlalchemy import Column, Integer, String, Date, Boolean, Enum as SQLEnum
from datetime import date
import enum
from ..database import Base

class TipoEmpleado(str, enum.Enum):
    DOCENTE = "Docente"
    APOYO = "Apoyo y Asistencia"

class Empleado(Base):
    __tablename__ = "empleados"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False, index=True)
    claves_presupuestales = Column(String, nullable=False)  # Puede tener múltiples, separadas por coma
    horario = Column(String, nullable=False)  # Ej: "08:00-15:00"
    adscripcion = Column(String, nullable=False)
    numero_asistencia = Column(String, nullable=False)
    tipo = Column(SQLEnum(TipoEmpleado), nullable=False)
    
    fecha_ingreso = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)
    
    # Contacto
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Empleado {self.nombre_completo}>"
    
    @property
    def antiguedad_meses(self) -> int:
        """Calcula antigüedad en meses"""
        hoy = date.today()
        meses = (hoy.year - self.fecha_ingreso.year) * 12
        meses += hoy.month - self.fecha_ingreso.month
        return meses
    
    @property
    def cumple_antiguedad_minima(self) -> bool:
        """Verifica si tiene 6 meses + 1 día de antigüedad"""
        return self.antiguedad_meses >= 6
```

### 6. app/utils/security.py
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica y valida un JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 7. app/utils/dependencies.py
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.user import User, UserRole
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

def require_role(required_roles: list[UserRole]):
    """Dependency para requerir ciertos roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Helpers para roles específicos
def get_current_root_user(current_user: User = Depends(require_role([UserRole.ROOT]))):
    return current_user

def get_current_admin_user(current_user: User = Depends(require_role([UserRole.ROOT, UserRole.ADMIN]))):
    return current_user
```

### 8. app/services/calendario_service.py
```python
from datetime import date, timedelta
from typing import List, Tuple
from ..config import settings

class CalendarioService:
    """Servicio para manejo de calendario laboral"""
    
    def __init__(self):
        self.festivos_2026 = self._cargar_festivos()
        self.vacaciones_2026 = self._cargar_vacaciones()
    
    def _cargar_festivos(self) -> List[date]:
        """Carga festivos desde config"""
        return [date(2026, mes, dia) for mes, dia in settings.FESTIVOS_2026]
    
    def _cargar_vacaciones(self) -> List[Tuple[date, date]]:
        """Carga períodos de vacaciones desde config"""
        periodos = []
        for inicio_str, fin_str in settings.VACACIONES_2026:
            inicio = date.fromisoformat(inicio_str)
            fin = date.fromisoformat(fin_str)
            periodos.append((inicio, fin))
        return periodos
    
    def es_fin_de_semana(self, fecha: date) -> bool:
        """Verifica si es sábado o domingo"""
        return fecha.weekday() >= 5  # 5=sábado, 6=domingo
    
    def es_festivo(self, fecha: date) -> bool:
        """Verifica si es día festivo oficial"""
        return fecha in self.festivos_2026
    
    def esta_en_vacaciones(self, fecha: date) -> bool:
        """Verifica si está en período de vacaciones administrativas"""
        for inicio, fin in self.vacaciones_2026:
            if inicio <= fecha <= fin:
                return True
        return False
    
    def es_dia_laboral(self, fecha: date) -> bool:
        """Verifica si es día laboral (no finde, no festivo, no vacaciones)"""
        if self.es_fin_de_semana(fecha):
            return False
        if self.es_festivo(fecha):
            return False
        if self.esta_en_vacaciones(fecha):
            return False
        return True
    
    def calcular_dias_laborales(self, fecha_inicio: date, fecha_fin: date) -> int:
        """
        Cuenta días laborales entre dos fechas (inclusivo)
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Número de días laborales
        """
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
        """
        Suma N días laborales a una fecha
        
        Args:
            fecha_inicio: Fecha de inicio
            num_dias: Número de días laborales a sumar
            
        Returns:
            Fecha resultante después de sumar días laborales
        """
        fecha_actual = fecha_inicio
        dias_contados = 0
        
        while dias_contados < num_dias:
            fecha_actual += timedelta(days=1)
            if self.es_dia_laboral(fecha_actual):
                dias_contados += 1
        
        return fecha_actual
    
    def obtener_siguiente_dia_laboral(self, fecha: date) -> date:
        """Obtiene el siguiente día laboral después de una fecha"""
        fecha_actual = fecha + timedelta(days=1)
        while not self.es_dia_laboral(fecha_actual):
            fecha_actual += timedelta(days=1)
        return fecha_actual
    
    def esta_en_periodo_bloqueado_vacaciones(
        self, 
        fecha: date, 
        dias_antes: int = 15, 
        dias_despues: int = 15
    ) -> bool:
        """
        Verifica si una fecha está en período bloqueado alrededor de vacaciones
        
        Args:
            fecha: Fecha a verificar
            dias_antes: Días laborales bloqueados antes de vacaciones
            dias_despues: Días laborales bloqueados después de vacaciones
        """
        for inicio_vac, fin_vac in self.vacaciones_2026:
            # Calcular fecha de bloqueo inicial (dias_antes laborales antes de inicio)
            fecha_bloqueo_inicio = inicio_vac
            dias_contados = 0
            while dias_contados < dias_antes:
                fecha_bloqueo_inicio -= timedelta(days=1)
                if self.es_dia_laboral(fecha_bloqueo_inicio):
                    dias_contados += 1
            
            # Calcular fecha de bloqueo final (dias_despues laborales después de fin)
            fecha_bloqueo_fin = fin_vac
            dias_contados = 0
            while dias_contados < dias_despues:
                fecha_bloqueo_fin += timedelta(days=1)
                if self.es_dia_laboral(fecha_bloqueo_fin):
                    dias_contados += 1
            
            # Verificar si fecha está en rango bloqueado
            if fecha_bloqueo_inicio <= fecha <= fecha_bloqueo_fin:
                return True
        
        return False

# Instancia global del servicio
calendario_service = CalendarioService()
```

### 9. app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import create_tables
from .routes import auth, empleados, justificantes

# Crear tablas al iniciar
create_tables()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
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

@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

---

## Frontend - Estructura Base

### 1. src/services/api.js
```javascript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. src/contexts/AuthContext.jsx
```javascript
import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Cargar usuario del localStorage al iniciar
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al iniciar sesión'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const hasRole = (roles) => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    hasRole,
    isAuthenticated: !!user,
    isRoot: user?.role === 'ROOT',
    isAdmin: user?.role === 'ADMIN' || user?.role === 'ROOT',
    isUsuario: user?.role === 'USUARIO'
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
```

### 3. src/components/common/ProtectedRoute.jsx
```javascript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};
```

### 4. src/App.jsx
```javascript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import Login from './pages/Login';
import DashboardEmpleado from './pages/DashboardEmpleado';
import DashboardRH from './pages/DashboardRH';
import DashboardRoot from './pages/DashboardRoot';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route
            path="/empleado/*"
            element={
              <ProtectedRoute allowedRoles={['USUARIO']}>
                <DashboardEmpleado />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/rh/*"
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'ROOT']}>
                <DashboardRH />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute allowedRoles={['ROOT']}>
                <DashboardRoot />
              </ProtectedRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

---

## Scripts Útiles

### scripts/create_root_user.py
```python
"""
Script para crear usuario ROOT inicial
Ejecutar una sola vez después de crear las tablas
"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

def create_root_user():
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario ROOT
        existing_root = db.query(User).filter(User.role == UserRole.ROOT).first()
        if existing_root:
            print("Ya existe un usuario ROOT")
            return
        
        # Crear usuario ROOT
        root_user = User(
            username="david",
            password_hash=get_password_hash("Admin123!"),  # CAMBIAR en producción
            role=UserRole.ROOT,
            active=True,
            password_changed=True  # Ya que estamos poniendo password inicial
        )
        
        db.add(root_user)
        db.commit()
        
        print("✓ Usuario ROOT creado exitosamente")
        print(f"  Username: {root_user.username}")
        print(f"  Password: Admin123!")
        print(f"  IMPORTANTE: Cambiar password en producción")
        
    except Exception as e:
        print(f"✗ Error al crear usuario ROOT: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_root_user()
```

### scripts/seed_test_data.py
```python
"""
Script para crear datos de prueba
"""
import sys
sys.path.append('.')

from datetime import date
from app.database import SessionLocal
from app.models.empleado import Empleado, TipoEmpleado
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

def seed_empleados():
    db = SessionLocal()
    
    empleados_test = [
        {
            "nombre_completo": "Juan Pérez García",
            "claves_presupuestales": "E3618.001234",
            "horario": "08:00-15:00",
            "adscripcion": "Coordinación Tecnológica",
            "numero_asistencia": "001",
            "tipo": TipoEmpleado.APOYO,
            "fecha_ingreso": date(2020, 1, 15),
            "email": "juan.perez@sep.gob.mx",
            "telefono": "2221234567"
        },
        {
            "nombre_completo": "María López Hernández",
            "claves_presupuestales": "E3618.001235",
            "horario": "08:00-15:00",
            "adscripcion": "Recursos Humanos",
            "numero_asistencia": "002",
            "tipo": TipoEmpleado.APOYO,
            "fecha_ingreso": date(2018, 3, 10),
            "email": "maria.lopez@sep.gob.mx",
            "telefono": "2221234568"
        },
        {
            "nombre_completo": "Pedro Martínez Sánchez",
            "claves_presupuestales": "E3618.001236",
            "horario": "08:00-14:00",
            "adscripcion": "Educación Básica",
            "numero_asistencia": "003",
            "tipo": TipoEmpleado.DOCENTE,
            "fecha_ingreso": date(2019, 8, 20),
            "email": "pedro.martinez@sep.gob.mx",
            "telefono": "2221234569"
        },
    ]
    
    try:
        for emp_data in empleados_test:
            empleado = Empleado(**emp_data)
            db.add(empleado)
        
        db.commit()
        print(f"✓ {len(empleados_test)} empleados de prueba creados")
        
        # Crear usuarios para los empleados
        empleados = db.query(Empleado).all()
        for emp in empleados:
            # Crear username a partir del nombre
            username = emp.nombre_completo.lower().replace(" ", ".").split(".")[0:2]
            username = ".".join(username)
            
            user = User(
                username=username,
                password_hash=get_password_hash("Temp123!"),
                role=UserRole.USUARIO,
                empleado_id=emp.id,
                active=True,
                password_changed=False
            )
            db.add(user)
        
        db.commit()
        print(f"✓ Usuarios creados para empleados")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_empleados()
```

---

## Notas Finales

Este código es un punto de partida. Desarrolla cada módulo completamente siguiendo las especificaciones del documento principal.

**Orden recomendado:**
1. Setup básico (config, database, models base)
2. Autenticación (security, dependencies, routes)
3. Calendario laboral (servicio crítico)
4. Validadores de justificantes
5. CRUD de empleados
6. Módulo de justificantes completo
7. Generación de PDFs
8. Frontend básico
9. Resto de módulos

**Tests después de cada módulo crítico.**

¡Éxito! 🚀
