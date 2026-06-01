# ExecutiveAI — Architecture Documentation

## System Overview

ExecutiveAI is a cloud-native analytics platform built on a microservice-oriented monolith with six layers:

```
┌──────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                          │
│                     Next.js 14 (App Router)                          │
│         Dashboards · Reports · AI Chat · Settings                    │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTPS / WebSocket
┌────────────────────────────▼─────────────────────────────────────────┐
│                           GATEWAY LAYER                              │
│                    Nginx 1.25 Reverse Proxy                          │
│          SSL Termination · Rate Limiting · Gzip · CORS               │
└──────────────┬──────────────────────────────┬────────────────────────┘
               │ /api/*                        │ /*
┌──────────────▼─────────────┐  ┌─────────────▼────────────────────────┐
│       API LAYER            │  │         STATIC / SSR LAYER            │
│   FastAPI (Python 3.11)    │  │          Next.js Server               │
└──────────────┬─────────────┘  └──────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────────────┐
│                         SERVICE LAYER                               │
│   Auth · Sales · Inventory · Forecasting · AI · Reports            │
└──────────┬───────────────────────────────────┬─────────────────────┘
           │                                   │
┌──────────▼──────────────┐     ┌──────────────▼────────────────────┐
│     DATA LAYER          │     │       ASYNC TASK LAYER            │
│  • PostgreSQL 15        │     │  • Celery Workers (4x)            │
│  • SQLAlchemy 2 (async) │     │  • Redis broker                   │
│  • Redis cache          │     │  • AI API calls                   │
└─────────────────────────┘     └──────────────────────────────────┘
```

---

## Tech Stack

### Backend
- **FastAPI** + **SQLAlchemy 2.0** (async) + **PostgreSQL 15**
- **LangGraph** ReAct agent with **Anthropic Claude**
- **Prophet** + **XGBoost** forecasting models
- **Celery** + **Redis** background task queue

### Frontend
- **Next.js 14** App Router, **React 19**, **TypeScript**
- **Tailwind CSS** + **shadcn/ui** components
- **Recharts** for data visualisation
- **Zustand** + **TanStack Query** for state management

---

## Security Model

- **JWT Bearer tokens** — 30-minute access tokens + 7-day refresh tokens
- **RBAC** with five roles: `superadmin`, `org_admin`, `executive`, `analyst`, `viewer`
- **Multi-tenancy**: schema-per-tenant isolation; `org_id` scoped at ORM level
- **TLS 1.2+** enforced at Nginx with HSTS
- All secrets loaded from environment variables

---

## Multi-Tenancy

Shared-database, schema-per-tenant design:

```
executiveai_db
├── public schema          ← shared tables (organisations, users)
├── org_001 schema         ← tenant A data
│   ├── sales_transactions
│   ├── inventory
│   └── ...
└── org_002 schema         ← tenant B data
```

Each API request resolves the organisation from the JWT token. SQLAlchemy sessions set `search_path` to the resolved schema, making cross-tenant queries structurally impossible.

---

## Scalability

| Component       | Scaling Strategy                              |
|-----------------|-----------------------------------------------|
| FastAPI backend | Add replicas; session-less JWT               |
| Celery workers  | Increase concurrency or add containers       |
| PostgreSQL      | Read replicas + PgBouncer connection pooling |
| Redis           | Redis Cluster or Sentinel for HA             |

**Performance optimisations:**
- KPI aggregates cached in Redis with 5-minute TTL
- AI responses cached by query hash (24-hour TTL)
- Composite indexes on `(org_id, created_at)` for time-series queries
- Heavy computations offloaded to Celery to keep API response times under 200ms
