from __future__ import annotations

from breakagent.modules.base import BaseModule
from breakagent.modules.quality import ContractModule, ResponseQualityModule
from breakagent.modules.robustness import EdgeCaseModule, ErrorHandlingModule
from breakagent.modules.security import AuthModule, BolaModule, InjectionModule

ALL_MODULES: list[type[BaseModule]] = [
    AuthModule,
    BolaModule,
    InjectionModule,
    EdgeCaseModule,
    ErrorHandlingModule,
    ContractModule,
    ResponseQualityModule,
]
