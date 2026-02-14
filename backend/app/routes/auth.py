from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import (
    ChangePasswordRequest,
    LoginResponse,
    ResetPasswordRequest,
    UserCreate,
    UserResponse,
)
from ..services.auth_service import (
    authenticate_user,
    change_password,
    create_user,
    reset_password,
    update_last_login,
)
from ..utils.dependencies import get_current_admin_user, get_current_root_user, get_current_user
from ..utils.helpers import registrar_auditoria
from ..utils.security import create_access_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None,
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    update_last_login(db, user)

    ip = request.client.host if request else None
    registrar_auditoria(db, user.id, user.username, "login", ip_address=ip)

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/change-password")
def change_password_endpoint(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = change_password(db, current_user, data.current_password, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Contrasena actual incorrecta")

    registrar_auditoria(
        db, current_user.id, current_user.username,
        "cambio_contrasena", "users", current_user.id,
    )
    return {"message": "Contrasena actualizada exitosamente"}


@router.post("/reset-password")
def reset_password_endpoint(
    data: ResetPasswordRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    user = reset_password(db, data.user_id, data.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"reset_contrasena de {user.username}", "users", user.id,
    )
    return {"message": f"Contrasena reseteada para {user.username}"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/usuarios", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(get_current_root_user),
    db: Session = Depends(get_db),
):
    return db.query(User).all()


@router.post("/usuarios", response_model=UserResponse)
def create_user_endpoint(
    data: UserCreate,
    current_user: User = Depends(get_current_root_user),
    db: Session = Depends(get_db),
):
    try:
        user = create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"creo usuario {user.username}", "users", user.id,
    )
    return user


@router.delete("/usuarios/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_root_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.role == UserRole.ROOT:
        raise HTTPException(status_code=400, detail="No se puede eliminar al usuario ROOT")

    user.active = False
    db.commit()

    registrar_auditoria(
        db, current_user.id, current_user.username,
        f"desactivo usuario {user.username}", "users", user.id,
    )
    return {"message": f"Usuario {user.username} desactivado"}
