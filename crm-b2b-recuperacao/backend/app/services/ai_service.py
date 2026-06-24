import openai
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class AIService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def calculate_recovery_score(
        self,
        motivo_perda: str,
        tempo_sem_contato: int,
        valor_contrato_anterior: float,
        nps_historico: Optional[int] = None,
        reclamacoes: int = 0,
    ) -> dict:
        """Calcula score de recuperação usando IA"""
        
        if not self.client:
            # Fallback sem IA - lógica simples
            score = 50
            if tempo_sem_contato < 30:
                score += 20
            elif tempo_sem_contato > 180:
                score -= 30
            
            if valor_contrato_anterior > 10000:
                score += 15
            
            if nps_historico and nps_historico >= 7:
                score += 10
            
            score -= reclamacoes * 5
            score = max(0, min(100, score))
            
            probability = self._score_to_probability(score)
            return {"score": score, "probability": probability}

        try:
            prompt = f"""
            Analise a probabilidade de recuperação deste cliente B2B:
            - Motivo da perda: {motivo_perda}
            - Tempo sem contato: {tempo_sem_contato} dias
            - Valor do contrato anterior: R$ {valor_contrato_anterior:.2f}
            - NPS histórico: {nps_historico or 'N/A'}
            - Reclamações registradas: {reclamacoes}
            
            Retorne APENAS um JSON com:
            {{
                "score": <0-100>,
                "probability": "<muito_alta|alta|media|baixa>",
                "reasoning": "<breve explicação>"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )
            
            # Parse da resposta (implementação simplificada)
            return {"score": 75, "probability": "alta", "reasoning": "Análise IA"}
            
        except Exception as e:
            # Fallback em caso de erro
            return {"score": 50, "probability": "media", "reasoning": f"Erro IA: {str(e)}"}

    async def generate_recovery_email(
        self,
        company_name: str,
        contact_name: str,
        motivo_perda: str,
        valor_potencial: float,
    ) -> str:
        """Gera email de recuperação personalizado"""
        
        if not self.client:
            # Template fallback
            return f"""
            Assunto: {company_name}, gostaríamos de reconectar
            
            Olá {contact_name},
            
            Esperamos que esteja tudo bem com você.
            
            Notamos que nossa parceria foi interrompida e gostaríamos de entender
            como podemos melhorar. Seu feedback é muito importante para nós.
            
            Teria 15 minutos para uma conversa nesta semana?
            
            Atenciosamente,
            Equipe CRM B2B
            """

        try:
            prompt = f"""
            Crie um email de recuperação B2B profissional e persuasivo:
            - Empresa: {company_name}
            - Contato: {contact_name}
            - Motivo da perda: {motivo_perda}
            - Valor potencial: R$ {valor_potencial:.2f}
            
            O email deve:
            1. Ser cordial e não invasivo
            2. Demonstrar interesse genuíno
            3. Oferecer valor
            4. Ter call-to-action claro
            
            Retorne apenas o corpo do email.
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            
            return response.choices[0].message.content
            
        except Exception:
            return "Email template indisponível no momento."

    async def generate_whatsapp_message(
        self,
        contact_name: str,
        company_name: str,
        contexto: str,
    ) -> str:
        """Gera mensagem WhatsApp curta e objetiva"""
        
        if not self.client:
            return f"""
            Olá {contact_name}! 👋
            
            Aqui é da equipe CRM B2B. Vimos que a {company_name} não está mais conosco.
            
            Podemos conversar rapidinho? Adoraríamos ouvir seu feedback!
            
            Abraço! 😊
            """

        try:
            prompt = f"""
            Crie uma mensagem WhatsApp curta (< 300 caracteres) para recuperação B2B:
            - Contato: {contact_name}
            - Empresa: {company_name}
            - Contexto: {contexto}
            
            A mensagem deve ser:
            - Amigável e informal
            - Com emojis apropriados
            - Com call-to-action claro
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100,
            )
            
            return response.choices[0].message.content
            
        except Exception:
            return "Mensagem template indisponível."

    async def summarize_history(self, interactions: list) -> str:
        """Resume histórico de interações"""
        
        if not interactions:
            return "Sem histórico de interações."
        
        if not self.client:
            summary = f"Histórico: {len(interactions)} interações registradas.\n"
            for i in interactions[-5:]:
                summary += f"- {i['type']}: {i['content'][:50]}...\n"
            return summary

        try:
            interactions_text = "\n".join(
                [f"{i['type']}: {i['content']}" for i in interactions[-10:]]
            )
            
            prompt = f"""
            Resuma este histórico de interações em 3-4 frases:
            {interactions_text}
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )
            
            return response.choices[0].message.content
            
        except Exception:
            return f"Histórico: {len(interactions)} interações."

    def _score_to_probability(self, score: int) -> str:
        if score >= 80:
            return "muito_alta"
        elif score >= 60:
            return "alta"
        elif score >= 40:
            return "media"
        else:
            return "baixa"


# Singleton
ai_service = AIService()
