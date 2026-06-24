from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CompanySizeEnum(str, Enum):
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class OpportunityStageEnum(str, Enum):
    PERDIDO = "perdido"
    IDENTIFICADO = "identificado"
    CONTATO_INICIADO = "contato_iniciado"
    DIAGNOSTICO = "diagnostico"
    NEGOCIACAO = "negociacao"
    PROPOSTA = "proposta"
    REATIVADO = "reativado"
    RECUPERADO = "recuperado"


class InteractionTypeEnum(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    LIGACAO = "ligacao"
    REUNIAO = "reuniao"
    VISITA = "visita"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Company Schemas
class CompanyBase(BaseModel):
    razao_social: str
    nome_fantasia: str
    cnpj: str
    segmento: str
    porte: CompanySizeEnum


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Contact Schemas
class ContactBase(BaseModel):
    name: str
    position: str
    email: EmailStr
    phone: str
    linkedin: Optional[str] = None
    is_primary: bool = False


class ContactCreate(ContactBase):
    company_id: int


class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Opportunity Schemas
class OpportunityBase(BaseModel):
    motivo_perda: str
    valor_potencial: float
    ai_score: Optional[int] = Field(default=50, ge=0, le=100)
    priority: Optional[str] = "media"


class OpportunityCreate(OpportunityBase):
    company_id: int
    owner_id: int


class OpportunityUpdate(BaseModel):
    stage: Optional[OpportunityStageEnum] = None
    ai_score: Optional[int] = None
    priority: Optional[str] = None
    next_followup_at: Optional[datetime] = None
    is_recovered: Optional[bool] = None


class OpportunityResponse(OpportunityBase):
    id: int
    company_id: int
    owner_id: int
    ai_probability: str
    stage: OpportunityStageEnum
    last_contact_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    is_recovered: bool
    recovered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Interaction Schemas
class InteractionBase(BaseModel):
    type: InteractionTypeEnum
    content: str
    outcome: Optional[str] = None


class InteractionCreate(InteractionBase):
    opportunity_id: int
    contact_id: int
    user_id: int


class InteractionResponse(InteractionBase):
    id: int
    opportunity_id: int
    contact_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Campaign Schemas
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    channel: str


class CampaignCreate(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: int
    status: str
    total_contacts: int
    converted: int
    conversion_rate: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardKPIs(BaseModel):
    receita_recuperada: float
    clientes_recuperados: int
    clientes_em_risco: int
    taxa_churn: float
    taxa_reativacao: float
    ticket_medio: float
    ltv_medio: float


class DashboardStats(BaseModel):
    total_opportunities: int
    by_stage: dict
    by_priority: dict
    recent_interactions: int
