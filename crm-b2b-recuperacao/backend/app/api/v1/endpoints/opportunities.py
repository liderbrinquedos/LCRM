from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models import RecoveryOpportunity, Company
from app.schemas import (
    OpportunityResponse,
    OpportunityCreate,
    OpportunityUpdate,
    DashboardKPIs,
    DashboardStats,
)
from app.repositories.opportunity_repository import OpportunityRepository
from app.services.ai_service import ai_service

router = APIRouter(prefix="/opportunities", tags=["Oportunidades"])


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    stage: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Lista todas as oportunidades de recuperação com filtros"""
    repo = OpportunityRepository(db)
    
    # Converter stage string para enum se necessário
    from app.schemas import OpportunityStageEnum
    stage_enum = None
    if stage:
        try:
            stage_enum = OpportunityStageEnum(stage.lower())
        except ValueError:
            pass
    
    opportunities = await repo.get_all(
        skip=skip,
        limit=limit,
        stage=stage_enum,
        priority=priority,
        search=search,
    )
    
    return opportunities


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtém detalhes de uma oportunidade específica"""
    repo = OpportunityRepository(db)
    opportunity = await repo.get_by_id(opportunity_id)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    
    return opportunity


@router.post("/", response_model=OpportunityResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Cria nova oportunidade de recuperação"""
    repo = OpportunityRepository(db)
    
    # Calcular score IA
    ai_result = await ai_service.calculate_recovery_score(
        motivo_perda=opportunity_data.motivo_perda,
        tempo_sem_contato=30,  # Default, ideal viria do input
        valor_contrato_anterior=opportunity_data.valor_potencial,
    )
    
    opportunity = RecoveryOpportunity(
        company_id=opportunity_data.company_id,
        owner_id=opportunity_data.owner_id,
        motivo_perda=opportunity_data.motivo_perda,
        valor_potencial=opportunity_data.valor_potencial,
        ai_score=ai_result["score"],
        ai_probability=ai_result["probability"],
        priority=opportunity_data.priority or "media",
    )
    
    created = await repo.create(opportunity)
    return created


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    updates: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza uma oportunidade existente"""
    repo = OpportunityRepository(db)
    opportunity = await repo.get_by_id(opportunity_id)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    
    update_dict = updates.model_dump(exclude_unset=True)
    updated = await repo.update(opportunity, update_dict)
    
    return updated


@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Remove uma oportunidade"""
    repo = OpportunityRepository(db)
    opportunity = await repo.get_by_id(opportunity_id)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
    
    await repo.delete(opportunity)
    return {"message": "Oportunidade removida com sucesso"}


@router.get("/stats/dashboard", response_model=dict)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Obtém estatísticas para o dashboard"""
    repo = OpportunityRepository(db)
    stats = await repo.get_stats()
    return stats


@router.get("/kpis", response_model=dict)
async def get_kpis(db: AsyncSession = Depends(get_db)):
    """Obtém KPIs principais"""
    repo = OpportunityRepository(db)
    kpis = await repo.get_kpis()
    return kpis
