from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models import RecoveryOpportunity, Company, Contact, Interaction, User, Campaign
from app.schemas import OpportunityStageEnum


class OpportunityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        stage: Optional[OpportunityStageEnum] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[RecoveryOpportunity]:
        query = select(RecoveryOpportunity).join(Company)

        if stage:
            query = query.where(RecoveryOpportunity.stage == stage)
        if priority:
            query = query.where(RecoveryOpportunity.priority == priority)
        if search:
            query = query.where(
                (Company.nome_fantasia.ilike(f"%{search}%")) |
                (Company.razao_social.ilike(f"%{search}%"))
            )

        query = query.offset(skip).limit(limit).order_by(RecoveryOpportunity.ai_score.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, opportunity_id: int) -> Optional[RecoveryOpportunity]:
        query = select(RecoveryOpportunity).where(RecoveryOpportunity.id == opportunity_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, opportunity: RecoveryOpportunity) -> RecoveryOpportunity:
        self.session.add(opportunity)
        await self.session.flush()
        await self.session.refresh(opportunity)
        return opportunity

    async def update(self, opportunity: RecoveryOpportunity, updates: dict) -> RecoveryOpportunity:
        for field, value in updates.items():
            setattr(opportunity, field, value)
        await self.session.flush()
        await self.session.refresh(opportunity)
        return opportunity

    async def delete(self, opportunity: RecoveryOpportunity) -> None:
        await self.session.delete(opportunity)

    async def get_stats(self) -> dict:
        # Total opportunities
        total_query = select(func.count(RecoveryOpportunity.id))
        total_result = await self.session.execute(total_query)
        total = total_result.scalar() or 0

        # By stage
        stage_query = select(
            RecoveryOpportunity.stage,
            func.count(RecoveryOpportunity.id)
        ).group_by(RecoveryOpportunity.stage)
        stage_result = await self.session.execute(stage_query)
        by_stage = {stage.value: count for stage, count in stage_result.all()}

        # By priority
        priority_query = select(
            RecoveryOpportunity.priority,
            func.count(RecoveryOpportunity.id)
        ).group_by(RecoveryOpportunity.priority)
        priority_result = await self.session.execute(priority_query)
        by_priority = {priority: count for priority, count in priority_result.all()}

        # Recent interactions
        recent_query = select(func.count(Interaction.id)).where(
            Interaction.created_at >= func.now() - func.interval('7 days')
        )
        recent_result = await self.session.execute(recent_query)
        recent_interactions = recent_result.scalar() or 0

        return {
            "total_opportunities": total,
            "by_stage": by_stage,
            "by_priority": by_priority,
            "recent_interactions": recent_interactions,
        }

    async def get_kpis(self) -> dict:
        # Clientes recuperados
        recovered_query = select(func.count(RecoveryOpportunity.id)).where(
            RecoveryOpportunity.is_recovered == True
        )
        recovered_result = await self.session.execute(recovered_query)
        clientes_recuperados = recovered_result.scalar() or 0

        # Receita recuperada
        revenue_query = select(func.sum(RecoveryOpportunity.valor_potencial)).where(
            RecoveryOpportunity.is_recovered == True
        )
        revenue_result = await self.session.execute(revenue_query)
        receita_recuperada = revenue_result.scalar() or 0.0

        # Em risco (stage inicial sem contato recente)
        risk_query = select(func.count(RecoveryOpportunity.id)).where(
            (RecoveryOpportunity.stage == OpportunityStageEnum.IDENTIFICADO) &
            ((RecoveryOpportunity.last_contact_at == None) | 
             (RecoveryOpportunity.last_contact_at < func.now() - func.interval('30 days')))
        )
        risk_result = await self.session.execute(risk_query)
        clientes_em_risco = risk_result.scalar() or 0

        # Ticket médio
        avg_ticket_query = select(func.avg(RecoveryOpportunity.valor_potencial)).where(
            RecoveryOpportunity.is_recovered == True
        )
        avg_ticket_result = await self.session.execute(avg_ticket_query)
        ticket_medio = avg_ticket_result.scalar() or 0.0

        return {
            "receita_recuperada": receita_recuperada,
            "clientes_recuperados": clientes_recuperados,
            "clientes_em_risco": clientes_em_risco,
            "taxa_churn": 0.0,  # Implementar lógica de churn
            "taxa_reativacao": 0.0,  # Implementar lógica de reativação
            "ticket_medio": ticket_medio,
            "ltv_medio": ticket_medio * 12,  # Estimativa anual
        }
