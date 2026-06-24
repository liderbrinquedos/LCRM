from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class CompanySize(enum.Enum):
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class OpportunityStage(enum.Enum):
    PERDIDO = "perdido"
    IDENTIFICADO = "identificado"
    CONTATO_INICIADO = "contato_iniciado"
    DIAGNOSTICO = "diagnostico"
    NEGOCIACAO = "negociacao"
    PROPOSTA = "proposta"
    REATIVADO = "reativado"
    RECUPERADO = "recuperado"


class InteractionType(enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    LIGACAO = "ligacao"
    REUNIAO = "reuniao"
    VISITA = "visita"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))  # admin, gestor, vendedor, customer_success
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    opportunities = relationship("RecoveryOpportunity", back_populates="owner")
    interactions = relationship("Interaction", back_populates="user")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    razao_social: Mapped[str] = mapped_column(String(255))
    nome_fantasia: Mapped[str] = mapped_column(String(255))
    cnpj: Mapped[str] = mapped_column(String(18), unique=True)
    segmento: Mapped[str] = mapped_column(String(100))
    porte: Mapped[CompanySize] = mapped_column(SQLEnum(CompanySize))
    status: Mapped[str] = mapped_column(String(50), default="ativo")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contacts = relationship("Contact", back_populates="company")
    opportunities = relationship("RecoveryOpportunity", back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    name: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    linkedin: Mapped[str] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="contacts")
    interactions = relationship("Interaction", back_populates="contact")


class RecoveryOpportunity(Base):
    __tablename__ = "recovery_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    motivo_perda: Mapped[str] = mapped_column(Text)
    ai_score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100
    ai_probability: Mapped[str] = mapped_column(String(20))  # muito_alta, alta, media, baixa
    valor_potencial: Mapped[float] = mapped_column(Float)
    stage: Mapped[OpportunityStage] = mapped_column(SQLEnum(OpportunityStage), default=OpportunityStage.IDENTIFICADO)
    priority: Mapped[str] = mapped_column(String(20), default="media")  # alta, media, baixa
    last_contact_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    next_followup_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_recovered: Mapped[bool] = mapped_column(Boolean, default=False)
    recovered_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="opportunities")
    owner = relationship("User", back_populates="opportunities")
    interactions = relationship("Interaction", back_populates="opportunity")


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(Integer, ForeignKey("recovery_opportunities.id"))
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    type: Mapped[InteractionType] = mapped_column(SQLEnum(InteractionType))
    content: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    opportunity = relationship("RecoveryOpportunity", back_populates="interactions")
    contact = relationship("Contact", back_populates="interactions")
    user = relationship("User", back_populates="interactions")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    channel: Mapped[str] = mapped_column(String(50))  # email, whatsapp, mixed
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, active, paused, completed
    total_contacts: Mapped[int] = mapped_column(Integer, default=0)
    converted: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
