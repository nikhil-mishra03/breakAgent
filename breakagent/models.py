from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from breakagent import __version__


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    OPEN = "open"
    FIXED = "fixed"


class Endpoint(BaseModel):
    path: str
    method: str
    requires_auth: bool = False
    parameters: list[str] = Field(default_factory=list)
    responses: dict[str, dict[str, object]] = Field(default_factory=dict)


class Finding(BaseModel):
    finding_id: str
    title: str
    module: str
    category: str
    severity: Severity
    confidence: Confidence
    description: str
    reproduction: str
    fix: str
    owasp: str | None = None
    endpoint: str | None = None
    status: FindingStatus = FindingStatus.OPEN


class BudgetConfig(BaseModel):
    request_budget: int = 500
    token_budget: int = 15000
    cost_cap_usd: float = 0.15
    timeout_seconds: int = 180


class ScanConfig(BaseModel):
    spec_path: str
    base_url: HttpUrl
    previous_report: str | None = None
    planner: str = "rule"
    llm_model: str = "gpt-5-mini"
    fail_on: Severity = Severity.MEDIUM
    budgets: BudgetConfig = Field(default_factory=BudgetConfig)


class ScanSummary(BaseModel):
    total_findings: int
    by_severity: dict[str, int]
    exit_code: int


class ScanResult(BaseModel):
    tool: str = "breakagent"
    version: str = __version__
    base_url: str
    findings: list[Finding]
    summary: ScanSummary
    budgets: BudgetConfig
    trace: list[str] = Field(default_factory=list)
