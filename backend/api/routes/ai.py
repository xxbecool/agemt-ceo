"""
AI routes: natural language query, insights generation, AI report generation.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from core.database import get_db
from api.deps import CurrentUser
from ai_agents.executive_agent import ExecutiveAgent
from schemas.ai import AIQueryRequest, AIQueryResponse, ReportGenerateRequest, ReportResponse

router = APIRouter()


@router.post("/query", response_model=AIQueryResponse)
async def ai_query(
    payload: AIQueryRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    agent = ExecutiveAgent(
        db=db,
        tenant_id=str(current_user.tenant_id),
        company_name="Acme Corporation",
    )
    result = await agent.query(payload.query)

    if isinstance(result, dict):
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        agent_steps = result.get("agent_steps", [])
        data_context = result.get("data_context")
    else:
        answer = str(result)
        sources = ["ai_agent"]
        agent_steps = []
        data_context = None

    return AIQueryResponse(
        query=payload.query,
        answer=answer,
        sources=sources,
        confidence=0.92,
        agent_steps=agent_steps if agent_steps else None,
        data_context=data_context,
        follow_up_suggestions=[
            "What are the top products this week?",
            "Show me branch performance comparison",
            "Are there any inventory alerts I should know about?",
        ],
    )


@router.get("/insights")
async def get_ai_insights(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    agent = ExecutiveAgent(
        db=db,
        tenant_id=str(current_user.tenant_id),
    )
    insights = await agent.generate_insights()
    return {
        "insights": insights,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "claude-sonnet-4-6",
        "count": len(insights),
    }


@router.post("/generate-report")
async def generate_ai_report(
    payload: ReportGenerateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    agent = ExecutiveAgent(
        db=db,
        tenant_id=str(current_user.tenant_id),
    )
    report = await agent.generate_report(payload.report_type)
    return report
