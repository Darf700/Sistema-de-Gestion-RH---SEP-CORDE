from sqlalchemy.orm import Session

from ..models.notificacion import Notificacion


def crear_notificacion(
    db: Session,
    usuario_id: int,
    tipo: str,
    mensaje: str,
    enlace: str = None,
):
    notif = Notificacion(
        usuario_id=usuario_id,
        tipo=tipo,
        mensaje=mensaje,
        enlace=enlace,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def obtener_notificaciones(db: Session, usuario_id: int, solo_no_leidas: bool = False):
    query = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id)
    if solo_no_leidas:
        query = query.filter(Notificacion.leida == False)
    return query.order_by(Notificacion.created_at.desc()).all()


def contar_no_leidas(db: Session, usuario_id: int) -> int:
    return (
        db.query(Notificacion)
        .filter(Notificacion.usuario_id == usuario_id, Notificacion.leida == False)
        .count()
    )


def marcar_leida(db: Session, notificacion_id: int, usuario_id: int) -> bool:
    notif = (
        db.query(Notificacion)
        .filter(Notificacion.id == notificacion_id, Notificacion.usuario_id == usuario_id)
        .first()
    )
    if not notif:
        return False
    notif.leida = True
    db.commit()
    return True


def marcar_todas_leidas(db: Session, usuario_id: int) -> int:
    count = (
        db.query(Notificacion)
        .filter(Notificacion.usuario_id == usuario_id, Notificacion.leida == False)
        .update({"leida": True})
    )
    db.commit()
    return count
