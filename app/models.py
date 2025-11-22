from typing import List, Optional
import datetime as dt  
from sqlalchemy import String, Integer, ForeignKey, Float, Date, Time, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum

# Flask-Login and password helpers
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass

class UserType(Enum):
    ADMIN = 0
    PEASANT = 1

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255))
    type: Mapped[UserType] = mapped_column(
        SAEnum(UserType),
        nullable=False,
        default=UserType.PEASANT
    )

    def set_password(self, raw_password: str) -> None:
        """Hash and store the password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Return True if password matches the stored hash."""
        if not self.password:
            return False
        return check_password_hash(self.password, raw_password)

    def __repr__(self) -> str:  # pragma: no cover - small convenience
        return f"<User id={self.id} login={self.login} type={self.type}>"

class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[Optional[str]] = mapped_column(String(200))
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    horses: Mapped[List["Horse"]] = relationship(back_populates="owner")


class Horse(Base):
    __tablename__ = "horses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(10))   # "male" / "female"
    age: Mapped[int] = mapped_column(Integer)

    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"))
    owner: Mapped["Owner"] = relationship(back_populates="horses")

    results: Mapped[List["Result"]] = relationship(back_populates="horse")


class Jockey(Base):
    __tablename__ = "jockeys"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[Optional[str]] = mapped_column(String(200))
    age: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float)

    results: Mapped[List["Result"]] = relationship(back_populates="jockey")


class Race(Base):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column(Date)
    time: Mapped[dt.time] = mapped_column(Time)
    place: Mapped[str] = mapped_column(String(120))
    title: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    results: Mapped[List["Result"]] = relationship(back_populates="race")


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"))
    horse_id: Mapped[int] = mapped_column(ForeignKey("horses.id"))
    jockey_id: Mapped[int] = mapped_column(ForeignKey("jockeys.id"))

    position: Mapped[int] = mapped_column(Integer)  # место в заезде
    race_time: Mapped[str] = mapped_column(String(20))  # время прохождения

    race: Mapped["Race"] = relationship(back_populates="results")
    horse: Mapped["Horse"] = relationship(back_populates="results")
    jockey: Mapped["Jockey"] = relationship(back_populates="results")
