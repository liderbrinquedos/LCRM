# CRM B2B - Recuperação Inteligente de Clientes

Plataforma CRM SaaS moderna especializada na recuperação, reativação e retenção de clientes B2B.

## Stack Tecnológica

### Frontend
- React 19 + Vite
- TypeScript
- Tailwind CSS
- Zustand (estado)
- Recharts (gráficos)
- Axios (API)

### Backend
- FastAPI
- Python 3.12+
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Redis
- Celery (tarefas assíncronas)

## Funcionalidades

### Dashboard Executivo
- KPIs em tempo real (Receita Recuperada, Clientes Recuperados, etc.)
- Gráficos de funil de recuperação
- Distribuição por prioridade
- Métricas de performance

### Pipeline de Recuperação
- Estágios: Perdido → Identificado → Contato → Diagnóstico → Negociação → Proposta → Reativado → Recuperado
- Score de IA para probabilidade de recuperação
- Priorização automática

### Inteligência Artificial
- Score preditivo de recuperação (0-100)
- Geração automática de emails
- Mensagens WhatsApp personalizadas
- Resumo de histórico de interações

## Como Rodar

### Opção 1: Docker Compose (Recomendado)

```bash
cd /workspace/crm-b2b-recuperacao
docker-compose up -d
```

Acesse:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Opção 2: Desenvolvimento Local

#### Backend
```bash
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Estrutura do Projeto

```
crm-b2b-recuperacao/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Rotas da API
│   │   ├── core/                # Configurações
│   │   ├── models/              # Modelos SQLAlchemy
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── repositories/        # Acesso a dados
│   │   ├── services/            # Serviços (IA, etc)
│   │   └── main.py              # Entry point
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── services/            # API client
│   │   ├── stores/              # Zustand stores
│   │   ├── lib/                 # Utilitários
│   │   └── App.tsx              # Componente principal
│   └── package.json
└── docker-compose.yml
```

## Endpoints da API

- `GET /api/v1/opportunities/` - Listar oportunidades
- `GET /api/v1/opportunities/{id}` - Detalhes da oportunidade
- `POST /api/v1/opportunities/` - Criar oportunidade
- `PATCH /api/v1/opportunities/{id}` - Atualizar oportunidade
- `GET /api/v1/opportunities/kpis` - KPIs do dashboard
- `GET /api/v1/opportunities/stats/dashboard` - Estatísticas

## Próximos Passos

1. [ ] Implementar autenticação JWT
2. [ ] Adicionar módulo de campanhas
3. [ ] Integração com WhatsApp Business API
4. [ ] Automações visuais (workflow builder)
5. [ ] Relatórios exportáveis (PDF, Excel)
6. [ ] Multi-tenant para SaaS

## License

MIT
