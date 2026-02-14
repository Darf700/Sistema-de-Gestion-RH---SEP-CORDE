"""Crea datos de prueba para desarrollo."""
import sys
sys.path.insert(0, ".")

from datetime import date

from app.database import SessionLocal, create_tables
from app.models.contador import Contador
from app.models.empleado import Empleado, TipoEmpleado, TipoNombramiento
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

create_tables()

db = SessionLocal()

EMPLEADOS = [
    {
        "nombre_completo": "Juan Perez Garcia",
        "claves_presupuestales": "E3618.001234",
        "horario": "08:00-15:00",
        "adscripcion": "Coordinacion Tecnologica",
        "numero_asistencia": "001",
        "tipo": TipoEmpleado.APOYO,
        "nombramiento": TipoNombramiento.BASE,
        "fecha_ingreso": date(2020, 1, 15),
        "email": "juan.perez@sep.gob.mx",
        "telefono": "2221234567",
    },
    {
        "nombre_completo": "Maria Lopez Hernandez",
        "claves_presupuestales": "E3618.001235",
        "horario": "08:00-15:00",
        "adscripcion": "Recursos Humanos",
        "numero_asistencia": "002",
        "tipo": TipoEmpleado.APOYO,
        "nombramiento": TipoNombramiento.BASE,
        "fecha_ingreso": date(2018, 3, 10),
        "email": "maria.lopez@sep.gob.mx",
        "telefono": "2221234568",
    },
    {
        "nombre_completo": "Pedro Martinez Sanchez",
        "claves_presupuestales": "E3618.001236",
        "horario": "08:00-14:00",
        "adscripcion": "Educacion Basica",
        "numero_asistencia": "003",
        "tipo": TipoEmpleado.DOCENTE,
        "nombramiento": TipoNombramiento.BASE,
        "fecha_ingreso": date(2019, 8, 20),
        "email": "pedro.martinez@sep.gob.mx",
        "telefono": "2221234569",
    },
    {
        "nombre_completo": "Ana Garcia Ruiz",
        "claves_presupuestales": "E3618.001237",
        "horario": "08:00-15:00",
        "adscripcion": "Recursos Humanos",
        "numero_asistencia": "004",
        "tipo": TipoEmpleado.APOYO,
        "nombramiento": TipoNombramiento.BASE,
        "fecha_ingreso": date(2017, 6, 1),
        "email": "ana.garcia@sep.gob.mx",
        "telefono": "2221234570",
    },
    {
        "nombre_completo": "Carlos Ramirez Torres",
        "claves_presupuestales": "E3618.001238",
        "horario": "08:00-15:00",
        "adscripcion": "Administracion",
        "numero_asistencia": "005",
        "tipo": TipoEmpleado.APOYO,
        "nombramiento": TipoNombramiento.BASE,
        "fecha_ingreso": date(2021, 2, 14),
        "email": "carlos.ramirez@sep.gob.mx",
        "telefono": "2221234571",
    },
]

try:
    anio = date.today().year

    for emp_data in EMPLEADOS:
        emp = Empleado(**emp_data)
        db.add(emp)
        db.flush()

        # Crear contador
        contador = Contador(empleado_id=emp.id, anio=anio)
        db.add(contador)

    db.commit()
    print(f"{len(EMPLEADOS)} empleados de prueba creados")

    # Crear usuarios ADMIN para las de RH
    rh_empleados = db.query(Empleado).filter(
        Empleado.adscripcion == "Recursos Humanos"
    ).all()
    for emp in rh_empleados:
        nombre_parts = emp.nombre_completo.lower().split()
        username = f"{nombre_parts[0]}.{nombre_parts[1]}"
        user = User(
            username=username,
            password_hash=get_password_hash("Temp123!"),
            role=UserRole.ADMIN,
            empleado_id=emp.id,
            active=True,
            password_changed=False,
        )
        db.add(user)
    db.commit()
    print(f"{len(rh_empleados)} usuarios ADMIN creados")

    # Crear usuarios USUARIO para el resto
    otros = db.query(Empleado).filter(
        Empleado.adscripcion != "Recursos Humanos"
    ).all()
    for emp in otros:
        nombre_parts = emp.nombre_completo.lower().split()
        username = f"{nombre_parts[0]}.{nombre_parts[1]}"
        user = User(
            username=username,
            password_hash=get_password_hash("Temp123!"),
            role=UserRole.USUARIO,
            empleado_id=emp.id,
            active=True,
            password_changed=False,
        )
        db.add(user)
    db.commit()
    print(f"{len(otros)} usuarios USUARIO creados")

    print("\nUsuarios creados:")
    print("  ROOT:    david / Admin123!")
    for u in db.query(User).filter(User.role != UserRole.ROOT).all():
        print(f"  {u.role.value:8s} {u.username} / Temp123!")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
    raise
finally:
    db.close()
