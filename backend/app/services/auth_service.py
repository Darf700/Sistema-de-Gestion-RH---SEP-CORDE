from datetime import datetime

from sqlalchemy.orm import Session

from ..models.user import User, UserRole
from ..schemas.user import UserCreate
from ..utils.security import get_password_hash, verify_password


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.active:
        return None
    return user


def create_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise ValueError(f"El usuario '{user_data.username}' ya existe")

    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        empleado_id=user_data.empleado_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    if not verify_password(current_password, user.password_hash):
        return False
    user.password_hash = get_password_hash(new_password)
    user.password_changed = True
    db.commit()
    return True


def reset_password(db: Session, user_id: int, new_password: str) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.password_hash = get_password_hash(new_password)
    user.password_changed = False
    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user: User):
    user.last_login = datetime.utcnow()
    db.commit()
