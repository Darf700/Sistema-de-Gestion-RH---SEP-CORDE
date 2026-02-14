"""Crea el usuario ROOT inicial. Ejecutar una sola vez."""
import sys
sys.path.insert(0, ".")

from app.database import SessionLocal, create_tables
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

create_tables()

db = SessionLocal()

try:
    existing = db.query(User).filter(User.role == UserRole.ROOT).first()
    if existing:
        print("Ya existe un usuario ROOT")
        sys.exit(0)

    root = User(
        username="david",
        password_hash=get_password_hash("Admin123!"),
        role=UserRole.ROOT,
        active=True,
        password_changed=True,
    )
    db.add(root)
    db.commit()

    print("Usuario ROOT creado exitosamente")
    print(f"  Username: david")
    print(f"  Password: Admin123!")
    print(f"  IMPORTANTE: Cambiar password en produccion")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
