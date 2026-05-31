# ExecutiveAI — Executive Analytics Platform

[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://postgresql.org)
[![Vercel](https://img.shields.io/badge/Vercel-Deploy-black?logo=vercel)](https://vercel.com)

**AI-powered executive analytics platform** — transforms business data into C-suite insights using Claude AI, real-time dashboards, predictive forecasting, and natural-language analysis.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Executive Dashboard** | KPI cards, revenue charts, trend indicators |
| 🤖 **AI Agent** | Ask questions in plain English — Claude answers with live data |
| 💰 **Sales Analytics** | Revenue breakdown, branch comparison, top products |
| 📦 **Inventory Intelligence** | Stock alerts, warehouse utilization, reorder predictions |
| 🔮 **Forecasting** | Revenue & demand forecasts via Prophet + XGBoost |
| 📋 **Report Engine** | Generate executive reports on demand |
| 🔐 **Multi-Tenant RBAC** | CEO / Admin / Manager / Analyst roles with full data isolation |

---

## 🚀 Deploy to Vercel (Frontend)

### One-click deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/xxbecool/agemt-ceo&root=frontend)

### Manual deploy

```bash
npm i -g vercel
cd frontend
vercel deploy
```

### Required Vercel environment variables

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://api.yourdomain.com` |
| `NEXT_PUBLIC_APP_NAME` | App display name | `ExecutiveAI` |

> **Note**: The frontend works fully with built-in mock data when no backend URL is set — perfect for UI demos.

---

## 🐳 Full Stack (Docker)

```bash
git clone https://github.com/xxbecool/agemt-ceo.git
cd agemt-ceo
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY
make setup
open http://localhost:3000
```

**Demo credentials:** `ceo@acme.com` / `password123`

### Services

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

---

## 🏗️ Architecture

```
Nginx (SSL · Rate Limit · Gzip)
  ├── /          → Next.js Frontend (React 19, TypeScript)
  └── /api/      → FastAPI Backend (Python 3.11)
                      │
           ┌─────────┼─────────┐
      PostgreSQL    Redis      Celery
                      │
                Anthropic Claude API (LangGraph)
```

---

## 🔧 Tech Stack

**Backend**: FastAPI, SQLAlchemy 2.0, PostgreSQL 15, Redis, Alembic, Celery  
**AI**: LangGraph ReAct agent, Anthropic Claude (`claude-sonnet-4-6`), Prophet, XGBoost  
**Frontend**: Next.js 14, React 19, TypeScript, Tailwind CSS, Recharts, Zustand, TanStack Query  
**Infrastructure**: Docker Compose, Nginx, Celery workers

---

## 📁 Project Structure

```
agemt-ceo/
├── frontend/          # Next.js 14 app (deploy to Vercel)
├── backend/           # FastAPI backend
├── infrastructure/    # Nginx config
├── docs/              # API & architecture docs
├── scripts/           # Setup & seed scripts
├── docker-compose.yml
├── vercel.json        # Vercel deployment config
└── Makefile
```

---

## 📖 API Reference

Full docs at `/docs` (Swagger).

```
POST  /api/v1/auth/login
GET   /api/v1/analytics/kpis
GET   /api/v1/sales/daily
GET   /api/v1/inventory/status
GET   /api/v1/forecasting/revenue
POST  /api/v1/ai/query
POST  /api/v1/reports/generate
```

---

## 📄 License

MIT
