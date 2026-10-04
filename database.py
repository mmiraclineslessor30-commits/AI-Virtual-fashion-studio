from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker


# SQLite database file
DATABASE_URL = "sqlite:///fashion_studio.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)

    height_cm = Column(Float, nullable=True)
    bust_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)

    preferred_fit = Column(String(100), nullable=True)
    preferred_colors = Column(Text, nullable=True)
    style_preferences = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class TryOnHistory(Base):
    __tablename__ = "tryon_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    garment_name = Column(String(255), nullable=True)

    person_image = Column(String(1000), nullable=True)
    garment_image = Column(String(1000), nullable=True)
    result_image = Column(String(1000), nullable=True)

    style_score = Column(Float, nullable=True)
    occasion = Column(String(100), nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


def init_db():
    """Create all database tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Create a database session."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    print("Database file: fashion_studio.db")
