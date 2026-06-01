# ExecutiveAI — API Reference

**Base URL:** `http://localhost:8000/api/v1`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Alternative Docs:** `http://localhost:8000/redoc`

---

## Table of Contents

- [Authentication](#authentication)
- [Dashboard](#dashboard)
- [Sales](#sales)
- [Inventory](#inventory)
- [AI Insights](#ai-insights)
- [Forecasting](#forecasting)
- [Reports](#reports)
- [Users](#users)
- [WebSocket](#websocket)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)

---

## Authentication

### POST /auth/login

Authenticate a user and receive access and refresh tokens.

**Request**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@executiveai.com&password=your_password
```

**Response — 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Response — 401 Unauthorized**
```json
{
  "detail": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}
```

---

### POST /auth/refresh

Exchange a refresh token for a new access token.

**Request**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### POST /auth/logout

Invalidate the current refresh token.

**Response — 204 No Content**

---

### GET /auth/me

Get the currently authenticated user's profile.

**Response — 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@executiveai.com",
  "full_name": "Jane Executive",
  "role": "org_admin",
  "organisation_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "is_active": true,
  "last_login_at": "2024-11-15T09:22:34Z",
  "created_at": "2024-01-10T08:00:00Z"
}
```

---

## Dashboard

### GET /dashboard/summary

Get top-level KPI summary for the current period.

**Query Parameters**
| Parameter   | Type   | Default | Description                            |
|-------------|--------|---------|----------------------------------------|
| `period`    | string | `month` | `day`, `week`, `month`, `quarter`, `year` |
| `date`      | date   | today   | Reference date (ISO 8601)              |

---

## Sales

### GET /sales/transactions

List sales transactions with filtering, sorting, and pagination.

### POST /sales/transactions

Create a new sales transaction.

### GET /sales/pipeline

Get sales pipeline grouped by stage.

### GET /sales/leaderboard

Sales rep performance leaderboard.

---

## Inventory

### GET /inventory/products

List inventory items.

### GET /inventory/alerts

Get inventory alert summary (low stock, out of stock).

### PATCH /inventory/products/{product_id}

Update inventory quantity or product details.

---

## AI Insights

### POST /ai/query

Submit a natural-language question to the AI engine.

**Request**
```json
{
  "question": "What are the top 3 reasons we lost deals this quarter?",
  "context": {
    "date_from": "2024-10-01",
    "date_to": "2024-12-31"
  }
}
```

**Response — 202 Accepted**
```json
{
  "task_id": "celery-task-uuid-...",
  "status": "pending",
  "estimated_seconds": 8
}
```

### GET /ai/result/{task_id}

Poll for AI query result.

### GET /ai/history

Retrieve past AI queries for the current user.

---

## Forecasting

### GET /forecast/revenue

Get revenue forecast for the next N periods.

### GET /forecast/demand/{product_id}

Get demand forecast for a specific inventory product.

### GET /forecast/churn

Get customer churn risk scores.

---

## Reports

### POST /reports/generate

Trigger on-demand report generation.

### GET /reports/{report_id}

Get report status and download URL.

### GET /reports

List generated reports.

---

## WebSocket

### WS /ws/{client_id}

Subscribe to real-time dashboard events.

**Incoming message types**

| Type               | Description                         |
|--------------------|-------------------------------------|
| `kpi_update`       | Updated KPI values (every 60s)      |
| `alert`            | Inventory or threshold alert        |
| `report_complete`  | Report generation finished          |
| `ai_result`        | AI query task completed             |

---

## Error Codes

| HTTP Status | Code                       | Description                                    |
|-------------|----------------------------|------------------------------------------------|
| 400         | `VALIDATION_ERROR`         | Request body failed Pydantic validation        |
| 401         | `INVALID_CREDENTIALS`      | Wrong email or password                        |
| 401         | `TOKEN_EXPIRED`            | JWT access token has expired                   |
| 403         | `PERMISSION_DENIED`        | User role does not permit this action          |
| 404         | `NOT_FOUND`                | Requested resource does not exist              |
| 429         | `RATE_LIMIT_EXCEEDED`      | Too many requests — see Retry-After header     |
| 500         | `INTERNAL_SERVER_ERROR`    | Unexpected server-side error                   |

---

## Rate Limiting

| Endpoint Group       | Limit                  |
|----------------------|------------------------|
| `/api/v1/auth/*`     | 5 requests / minute    |
| `/api/v1/ai/*`       | 20 requests / minute   |
| All other `/api/*`   | 30 requests / second   |
| Frontend `/*`        | 100 requests / second  |
