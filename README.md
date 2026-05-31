# ExecutiveAI — Executive Analytics Platform

AI-powered executive analytics platform for CEOs and operations teams.

## Quick Start

```bash
cp .env.example .env
make setup
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Demo login: `ceo@acme.com` / `password123`

## Stack
- **Backend**: FastAPI, PostgreSQL 15, Redis 7, Celery, Alembic
- **AI**: LangGraph ReAct agent, Anthropic Claude
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Recharts
- **Infra**: Docker Compose, Nginx
