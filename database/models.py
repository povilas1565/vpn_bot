from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Column
import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    start_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    expire_date: Mapped[datetime.datetime]
    status: Mapped[str] = mapped_column(default="active")  # active / expired
    balance: Mapped[float] = mapped_column(default=0.0)

    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))
    server: Mapped["Server"] = relationship(back_populates="users")

    vpn_keys: Mapped[list["VPNKey"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(nullable=False)
    ssh_user: Mapped[str] = mapped_column(nullable=False)
    ssh_password: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)  # Base / Silver / Gold
    users_count: Mapped[int] = mapped_column(default=0)
    max_users: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="active")
    server_public_key: Mapped[str] = mapped_column(nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="server", cascade="all, delete")

class VPNKey(Base):
    __tablename__ = "vpn_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    private_key: Mapped[str]
    public_key: Mapped[str]
    allowed_ip: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="vpn_keys")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]
    amount: Mapped[float]
    date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    status: Mapped[str]  # pending / confirmed / failed
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="payments")