from sqlalchemy.orm import Session

from database import User, TryOnHistory


def create_user(db: Session, user_data):
    user = User(**user_data.dict())

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(db: Session, user_id: int):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_all_users(db: Session):
    return db.query(User).all()


def create_tryon(db: Session, tryon_data):
    record = TryOnHistory(**tryon_data.dict())

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_tryon_history(db: Session):
    return (
        db.query(TryOnHistory)
        .order_by(TryOnHistory.id.desc())
        .all()
    )