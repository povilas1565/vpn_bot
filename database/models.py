from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Column
import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    start_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    expire_date: Mapped[datetime.datetime]
    status: Mapped[str] = mapped_column(default="active")  # active / expired
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))
    vpn_key = relationship("VPNKey", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Server(Base):
    __tablename__ = "servers"
    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str]
    ssh_user = Column(String, nullable=False)          # <- добавляем
    ssh_password = Column(String, nullable=False)      # <- добавляем
    type: Mapped[str]  # Base / Silver / Gold
    users_count: Mapped[int] = mapped_column(default=0)
    max_users: Mapped[int]
    status: Mapped[str] = mapped_column(default="active")

class VPNKey(Base):
    __tablename__ = "vpn_keys"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    private_key: Mapped[str]
    public_key: Mapped[str]
    allowed_ip: Mapped[str]

    user = relationship("User", back_populates="vpn_key")

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    ip = Column(String, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]
    amount: Mapped[float]
    date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    status: Mapped[str]  # pending / confirmed / failed
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="payments")