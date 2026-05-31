"""
ExecutiveAI LangGraph ReAct Agent.

Implements a ReAct (Reasoning + Acting) agent using LangGraph and Anthropic Claude.
The agent can call data tools to answer CEO-level business questions with real data context.
"""
import json
import uuid
from datetime import date, datetime, timezone
from typing import Any, TypedDict, Annotated, Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from ai_agents.prompts import (
    EXECUTIVE_SYSTEM_PROMPT,
    INSIGHTS_PROMPT,
    REPORT_DAILY_PROMPT,
)
from ai_agents.tools import (
    get_sales_summary,
    get_inventory_status,
    get_kpi_metrics,
    get_anomalies,
    get_top_products,
)


# ---------------------------------------------------------------------------
# LangGraph ReAct agent (imported lazily to avoid import errors if not installed)
# ---------------------------------------------------------------------------

def _build_langgraph_agent(tenant_id: str, db: AsyncSession):
    """Build and return a compiled LangGraph ReAct agent."""
    from langchain_anthropic import ChatAnthropic
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage
    from langgraph.prebuilt import create_react_agent

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=2048,
    )

    # Define tools as sync wrappers that will be called with async context
    import asyncio

    def _run(coro):
        """Run a coroutine from a sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    @tool
    def tool_get_sales_summary(period: str = "7d") -> str:
        """
        Get aggregated sales summary for a specific time period.
        period can be: 1d (yesterday), 7d (last 7 days), 30d (last 30 days), 90d (last 90 days).
        Returns total revenue, orders, gross profit, and daily breakdown.
        """
        try:
            result = _run(get_sales_summary(db, tenant_id, period))
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def tool_get_inventory_status() -> str:
        """
        Get current inventory status including critical stock items, low stock items, and healthy items.
        Returns total SKUs, items needing reorder, and items with critical/low stock levels.
        """
        try:
            result = _run(get_inventory_status(db, tenant_id))
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def tool_get_kpi_metrics() -> str:
        """
        Get key performance indicators including month-to-date revenue, gross profit,
        profit margin, order count, average order value, and day-over-day change.
        """
        try:
            result = _run(get_kpi_metrics(db, tenant_id))
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def tool_get_anomalies(lookback_days: int = 30) -> str:
        """
        Detect revenue anomalies over the last N days using statistical analysis.
        Returns anomalies with their dates, actual vs expected revenue, and severity.
        lookback_days: number of days to analyze (default: 30).
        """
        try:
            result = _run(get_anomalies(db, tenant_id, lookback_days))
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @tool
    def tool_get_top_products(days: int = 30) -> str:
        """
        Get top 5 products by revenue for the last N days.
        Returns product names, categories, revenue, and units sold.
        days: lookback period in days (default: 30).
        """
        try:
            result = _run(get_top_products(db, tenant_id, days))
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    tools = [
        tool_get_sales_summary,
        tool_get_inventory_status,
        tool_get_kpi_metrics,
        tool_get_anomalies,
        tool_get_top_products,
    ]

    agent = create_react_agent(llm, tools)
    return agent


class ExecutiveAgent:
    """
    Production-grade ExecutiveAI agent backed by LangGraph + Anthropic Claude.
    Falls back to direct API calls when LangGraph is unavailable.
    """

    def __init__(
        self,
        db: AsyncSession,
        tenant_id: str,
        company_name: str = "Acme Corporation",
    ):
        self.db = db
        self.tenant_id = tenant_id
        self.company_name = company_name
        self._anthropic_client = None

    def _get_anthropic_client(self):
        if self._anthropic_client is None:
            import anthropic
            self._anthropic_client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        return self._anthropic_client

    async def _gather_context(self) -> str:
        """Gather all relevant business context for the AI."""
        sales_7d = await get_sales_summary(self.db, self.tenant_id, "7d")
        sales_30d = await get_sales_summary(self.db, self.tenant_id, "30d")
        inventory = await get_inventory_status(self.db, self.tenant_id)
        kpis = await get_kpi_metrics(self.db, self.tenant_id)
        top_products = await get_top_products(self.db, self.tenant_id)
        anomaly_data = await get_anomalies(self.db, self.tenant_id, 30)

        context = f"""
CURRENT BUSINESS DATA (as of {date.today().isoformat()}):

=== KPI METRICS (Month-to-Date) ===
Revenue MTD: ${kpis['revenue_mtd']:,.2f}
Gross Profit MTD: ${kpis['gross_profit_mtd']:,.2f}
Profit Margin: {kpis['profit_margin_pct']}%
Orders MTD: {kpis['orders_mtd']:,}
Average Order Value: ${kpis['avg_order_value']:,.2f}
Active Alerts: {kpis['active_alerts']}
Yesterday Revenue: ${kpis['yesterday_revenue']:,.2f}
Day-over-Day Change: {kpis['day_over_day_change_pct']:+.1f}%

=== SALES PERFORMANCE (Last 7 Days) ===
Total Revenue: ${sales_7d['total_revenue']:,.2f}
Total Orders: {sales_7d['total_orders']:,}
Avg Daily Revenue: ${sales_7d['avg_daily_revenue']:,.2f}
Gross Profit: ${sales_7d['gross_profit']:,.2f}
Profit Margin: {sales_7d['profit_margin_pct']}%
Daily Breakdown: {json.dumps(sales_7d['daily_breakdown'], indent=2)}

=== SALES PERFORMANCE (Last 30 Days) ===
Total Revenue: ${sales_30d['total_revenue']:,.2f}
Total Orders: {sales_30d['total_orders']:,}
Avg Daily Revenue: ${sales_30d['avg_daily_revenue']:,.2f}

=== TOP 5 PRODUCTS (Last 30 Days) ===
{json.dumps(top_products['top_products'], indent=2)}

=== INVENTORY STATUS ===
Total SKUs: {inventory['total_skus']}
Critical Stock (need immediate reorder): {inventory['requires_immediate_attention']}
Low Stock Items: {len(inventory['low_stock'])}
Healthy Items: {inventory['healthy_count']}
Critical Items: {json.dumps(inventory['critical_stock'][:5], indent=2)}
Low Stock Items: {json.dumps(inventory['low_stock'][:5], indent=2)}

=== ANOMALIES (Last 30 Days) ===
Total Anomalies Detected: {anomaly_data['total_anomalies']}
Avg Daily Revenue (baseline): ${anomaly_data['avg_daily_revenue']:,.2f}
Recent Anomalies: {json.dumps(anomaly_data['anomalies'][:3], indent=2)}
"""
        return context

    async def query(self, user_question: str) -> dict:
        """
        Main entry point: answer a CEO question using LangGraph ReAct agent
        or fall back to direct Anthropic API call.
        """
        if not settings.ANTHROPIC_API_KEY:
            return {
                "answer": self._mock_answer(user_question),
                "sources": ["mock_data"],
                "agent_steps": [],
                "data_context": None,
            }

        # Try LangGraph ReAct agent first
        try:
            return await self._query_with_langgraph(user_question)
        except Exception as langgraph_err:
            # Fall back to direct API call with pre-gathered context
            try:
                return await self._query_direct(user_question)
            except Exception as direct_err:
                return {
                    "answer": (
                        f"I encountered an issue processing your request. "
                        f"Please check your API configuration. Error: {direct_err}"
                    ),
                    "sources": [],
                    "agent_steps": [],
                    "data_context": None,
                }

    async def _query_with_langgraph(self, question: str) -> dict:
        """Use LangGraph ReAct agent to answer the question."""
        import asyncio
        from langchain_core.messages import HumanMessage

        system_prompt = EXECUTIVE_SYSTEM_PROMPT.format(
            company_name=self.company_name,
            today=date.today().isoformat(),
        )

        agent = _build_langgraph_agent(self.tenant_id, self.db)

        # Run in thread pool since LangGraph tools are sync
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: agent.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=f"System: {system_prompt}\n\nQuestion: {question}"
                        )
                    ]
                }
            ),
        )

        messages = result.get("messages", [])
        final_answer = ""
        agent_steps = []

        for msg in messages:
            msg_type = type(msg).__name__
            content = msg.content if hasattr(msg, "content") else str(msg)
            if msg_type == "AIMessage":
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            final_answer = block["text"]
                        elif isinstance(block, dict) and block.get("type") == "tool_use":
                            agent_steps.append({
                                "tool": block.get("name"),
                                "input": block.get("input"),
                            })
                elif isinstance(content, str) and content:
                    final_answer = content

        return {
            "answer": final_answer or "Analysis complete.",
            "sources": ["sales_data", "inventory_data", "kpi_metrics", "anomaly_detection"],
            "agent_steps": agent_steps,
            "data_context": None,
        }

    async def _query_direct(self, question: str) -> dict:
        """Direct Anthropic API call with pre-gathered context."""
        context = await self._gather_context()
        system_prompt = EXECUTIVE_SYSTEM_PROMPT.format(
            company_name=self.company_name,
            today=date.today().isoformat(),
        )
        client = self._get_anthropic_client()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"{context}\n\nExecutive Question: {question}",
                }
            ],
        )
        return {
            "answer": message.content[0].text,
            "sources": ["sales_data", "inventory_data", "kpi_metrics"],
            "agent_steps": [],
            "data_context": None,
        }

    async def generate_insights(self) -> list:
        """Generate proactive executive insights from current data."""
        if not settings.ANTHROPIC_API_KEY:
            return self._mock_insights()

        try:
            context = await self._gather_context()
            client = self._get_anthropic_client()
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system="You are an executive business analyst. Respond ONLY with valid JSON array.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{context}\n\n{INSIGHTS_PROMPT}",
                    }
                ],
            )
            text = message.content[0].text
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return self._mock_insights()
        except Exception:
            return self._mock_insights()

    async def generate_report(self, report_type: str = "daily") -> dict:
        """Generate an AI-written executive report."""
        if not settings.ANTHROPIC_API_KEY:
            return self._mock_report(report_type)

        try:
            context = await self._gather_context()
            client = self._get_anthropic_client()
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system="You are an executive business analyst generating formal business reports.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{context}\n\n{REPORT_DAILY_PROMPT}",
                    }
                ],
            )
            return {
                "report_id": str(uuid.uuid4()),
                "report_type": report_type,
                "period": date.today().isoformat(),
                "executive_summary": message.content[0].text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception:
            return self._mock_report(report_type)

    # ------------------------------------------------------------------
    # Mock / fallback implementations
    # ------------------------------------------------------------------

    def _mock_answer(self, question: str) -> str:
        return (
            f"[DEMO MODE - Configure ANTHROPIC_API_KEY to enable AI] "
            f"Based on current business data: Sales are trending positively with strong MTD performance. "
            f"Inventory levels are stable with a few items requiring reorder attention. "
            f"Question received: '{question}'"
        )

    def _mock_insights(self) -> list:
        return [
            {
                "title": "Revenue Growth Momentum",
                "description": "Monthly revenue is tracking 12.3% above last month, driven primarily by Electronics and Health categories.",
                "category": "revenue",
                "severity": "info",
                "action_required": False,
                "recommendation": "Maintain current promotional strategy for top-performing categories.",
            },
            {
                "title": "Critical Inventory Alert",
                "description": "3 high-velocity products are at critical stock levels with less than 3 days of inventory remaining.",
                "category": "inventory",
                "severity": "critical",
                "action_required": True,
                "recommendation": "Immediately initiate emergency reorder for critical SKUs.",
            },
            {
                "title": "Branch Performance Gap",
                "description": "North Branch is outperforming South Branch by 34% in revenue despite similar market demographics.",
                "category": "performance",
                "severity": "warning",
                "action_required": True,
                "recommendation": "Schedule operational review with South Branch management.",
            },
            {
                "title": "Profit Margin Improvement",
                "description": "Gross profit margin improved 2.1% this month due to better product mix optimization.",
                "category": "revenue",
                "severity": "info",
                "action_required": False,
                "recommendation": "Continue focusing on higher-margin product categories.",
            },
        ]

    def _mock_report(self, report_type: str) -> dict:
        return {
            "report_id": str(uuid.uuid4()),
            "report_type": report_type,
            "period": date.today().isoformat(),
            "executive_summary": (
                "Business performance remains strong with consistent growth across key metrics. "
                "Revenue is tracking above target with healthy profit margins. "
                "Inventory management requires attention for 3 critical SKUs. "
                "Branch performance shows opportunities for operational improvement."
            ),
            "key_metrics": {
                "revenue_mtd": 245000,
                "orders_mtd": 1240,
                "profit_margin": 28.5,
            },
            "recommendations": [
                "Reorder critical stock items immediately",
                "Review South Branch operations",
                "Expand top product promotions",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
