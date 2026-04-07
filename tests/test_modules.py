from __future__ import annotations

import pytest

from breakagent.models import Endpoint
from breakagent.modules.quality import ContractModule, ResponseQualityModule
from breakagent.modules.robustness import EdgeCaseModule, ErrorHandlingModule
from breakagent.modules.security import AuthModule, BolaModule, InjectionModule


def _ep(
    path: str = "/items",
    method: str = "get",
    requires_auth: bool = False,
    parameters: list[str] | None = None,
    responses: dict[str, dict[str, object]] | None = None,
) -> Endpoint:
    return Endpoint(
        path=path,
        method=method,
        requires_auth=requires_auth,
        parameters=parameters or [],
        responses=responses or {},
    )


# ---------------------------------------------------------------------------
# AuthModule
# ---------------------------------------------------------------------------

class TestAuthModule:
    def test_flags_unauthenticated_admin_endpoint(self) -> None:
        findings = AuthModule().run([_ep(path="/admin/users")])
        assert len(findings) == 1
        assert findings[0].finding_id == "AUTH-get-/admin/users"
        assert findings[0].severity.value == "high"

    def test_ignores_authenticated_admin_endpoint(self) -> None:
        findings = AuthModule().run([_ep(path="/admin/users", requires_auth=True)])
        assert findings == []

    def test_ignores_non_admin_endpoint(self) -> None:
        findings = AuthModule().run([_ep(path="/items")])
        assert findings == []

    def test_module_name(self) -> None:
        assert AuthModule.name == "auth"


# ---------------------------------------------------------------------------
# BolaModule
# ---------------------------------------------------------------------------

class TestBolaModule:
    def test_flags_unauthenticated_id_endpoint(self) -> None:
        findings = BolaModule().run([_ep(path="/items/{id}")])
        assert len(findings) == 1
        assert findings[0].finding_id == "BOLA-get-/items/{id}"
        assert findings[0].owasp == "API1:2023"

    def test_flags_non_id_path_params(self) -> None:
        for path in ["/orders/{orderId}", "/users/{username}", "/pets/{petId}"]:
            findings = BolaModule().run([_ep(path=path)])
            assert len(findings) == 1, f"Expected finding for {path}"

    def test_ignores_authenticated_id_endpoint(self) -> None:
        findings = BolaModule().run([_ep(path="/items/{id}", requires_auth=True)])
        assert findings == []

    def test_ignores_endpoint_without_path_params(self) -> None:
        findings = BolaModule().run([_ep(path="/items")])
        assert findings == []

    def test_reproduction_uses_resolved_path(self) -> None:
        findings = BolaModule().run([_ep(path="/orders/{orderId}")])
        assert "/orders/1" in findings[0].reproduction

    def test_module_name(self) -> None:
        assert BolaModule.name == "bola"


# ---------------------------------------------------------------------------
# InjectionModule
# ---------------------------------------------------------------------------

class TestInjectionModule:
    @pytest.mark.parametrize("param", ["query", "search", "filter", "QUERY", "Search"])
    def test_flags_injectable_param(self, param: str) -> None:
        findings = InjectionModule().run([_ep(parameters=[param])])
        assert len(findings) == 1

    def test_ignores_safe_params(self) -> None:
        findings = InjectionModule().run([_ep(parameters=["id", "page", "limit"])])
        assert findings == []

    def test_no_params_produces_no_finding(self) -> None:
        findings = InjectionModule().run([_ep()])
        assert findings == []

    def test_module_name(self) -> None:
        assert InjectionModule.name == "injection"


# ---------------------------------------------------------------------------
# EdgeCaseModule
# ---------------------------------------------------------------------------

class TestEdgeCaseModule:
    @pytest.mark.parametrize("method", ["post", "put", "patch"])
    def test_flags_write_method_without_responses(self, method: str) -> None:
        findings = EdgeCaseModule().run([_ep(method=method, responses={})])
        assert len(findings) == 1
        assert findings[0].category == "robustness"

    def test_ignores_write_method_with_responses(self) -> None:
        findings = EdgeCaseModule().run([_ep(method="post", responses={"200": {"description": "ok"}})])
        assert findings == []

    def test_ignores_get_without_responses(self) -> None:
        findings = EdgeCaseModule().run([_ep(method="get", responses={})])
        assert findings == []

    def test_module_name(self) -> None:
        assert EdgeCaseModule.name == "edgecase"


# ---------------------------------------------------------------------------
# ErrorHandlingModule
# ---------------------------------------------------------------------------

class TestErrorHandlingModule:
    def test_flags_endpoint_with_no_error_codes(self) -> None:
        findings = ErrorHandlingModule().run([_ep(responses={"200": {"description": "ok"}})])
        assert len(findings) == 1
        assert findings[0].severity.value == "low"

    def test_ignores_endpoint_with_4xx(self) -> None:
        findings = ErrorHandlingModule().run([_ep(responses={"200": {}, "400": {}})])
        assert findings == []

    def test_ignores_endpoint_with_5xx(self) -> None:
        findings = ErrorHandlingModule().run([_ep(responses={"200": {}, "500": {}})])
        assert findings == []

    def test_flags_endpoint_with_no_responses_at_all(self) -> None:
        findings = ErrorHandlingModule().run([_ep(responses={})])
        assert len(findings) == 1

    def test_module_name(self) -> None:
        assert ErrorHandlingModule.name == "errorhandling"


# ---------------------------------------------------------------------------
# ContractModule
# ---------------------------------------------------------------------------

class TestContractModule:
    def test_flags_endpoint_missing_responses(self) -> None:
        findings = ContractModule().run([_ep(responses={})])
        assert len(findings) == 1
        assert findings[0].confidence.value == "high"

    def test_ignores_endpoint_with_responses(self) -> None:
        findings = ContractModule().run([_ep(responses={"200": {"description": "ok"}})])
        assert findings == []

    def test_module_name(self) -> None:
        assert ContractModule.name == "contract"


# ---------------------------------------------------------------------------
# ResponseQualityModule
# ---------------------------------------------------------------------------

class TestResponseQualityModule:
    def test_flags_200_without_description(self) -> None:
        findings = ResponseQualityModule().run([_ep(responses={"200": {"schema": {}}})])
        assert len(findings) == 1
        assert findings[0].severity.value == "info"

    def test_ignores_200_with_description(self) -> None:
        findings = ResponseQualityModule().run([_ep(responses={"200": {"description": "ok"}})])
        assert findings == []

    def test_ignores_endpoint_without_200(self) -> None:
        findings = ResponseQualityModule().run([_ep(responses={"201": {}})])
        assert findings == []

    def test_module_name(self) -> None:
        assert ResponseQualityModule.name == "responsequality"


# ---------------------------------------------------------------------------
# Shared: _make_finding populates module and endpoint fields
# ---------------------------------------------------------------------------

def test_make_finding_sets_module_and_endpoint_from_base() -> None:
    ep = _ep(path="/admin/users", method="get")
    findings = AuthModule().run([ep])
    assert findings[0].module == "auth"
    assert findings[0].endpoint == "GET /admin/users"
