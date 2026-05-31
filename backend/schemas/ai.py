from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class AIQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    include_data: bool = True


class AIQueryResponse(BaseModel):
    query: str
    answer: str
    data_context: Optional[Dict[str, Any]] = None
    sources: List[str] = []
    confidence: Optional[float] = None
    follow_up_suggestions: List[str] = []
    agent_steps: Optional[List[Dict[str, Any]]] = None


class ReportGenerateRequest(BaseModel):
    report_type: str  # daily, weekly, monthly, quarterly, custom
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    include_sections: List[str] = ["sales", "inventory", "kpis", "forecasts", "alerts"]
    format: str = "json"  # json, pdf, excel
    recipient_email: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: str
    report_type: str
    generated_at: str
    period_start: str
    period_end: str
    sections: Dict[str, Any]
    summary: str
    download_url: Optional[str] = None
