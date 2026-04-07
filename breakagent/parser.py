from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from breakagent.models import Endpoint

logger = logging.getLogger(__name__)


class SpecParseError(ValueError):
    pass


_SUPPORTED_METHODS: frozenset[str] = frozenset({"get", "post", "put", "patch", "delete"})


def _load_spec(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(text)
        else:
            data = json.loads(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        logger.error("spec_parse_failed path=%s error=%s", path, exc)
        raise SpecParseError(f"Unable to parse OpenAPI spec: {exc}") from exc
    if not isinstance(data, dict) or "paths" not in data:
        raise SpecParseError("OpenAPI spec must contain a top-level 'paths' object")
    return data  # type: ignore[return-value]


def parse_openapi(path: str) -> list[Endpoint]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise SpecParseError(f"Spec file not found: {path}")

    data = _load_spec(spec_path)
    paths = data.get("paths", {})
    endpoints: list[Endpoint] = []

    for route, route_spec in paths.items():
        if not isinstance(route_spec, dict):
            continue
        for method, method_spec in route_spec.items():
            if method.lower() not in _SUPPORTED_METHODS:
                continue
            if not isinstance(method_spec, dict):
                continue

            security = method_spec.get("security")
            requires_auth = bool(security)
            params = [p.get("name", "") for p in method_spec.get("parameters", []) if isinstance(p, dict)]
            responses_raw = method_spec.get("responses", {})
            responses: dict[str, dict[str, object]] = {}
            if isinstance(responses_raw, dict):
                for code, value in responses_raw.items():
                    if isinstance(value, dict):
                        responses[str(code)] = value
            try:
                endpoints.append(
                    Endpoint(
                        path=route,
                        method=method.lower(),
                        requires_auth=requires_auth,
                        parameters=[p for p in params if p],
                        responses=responses,
                    )
                )
            except ValidationError as exc:
                raise SpecParseError(
                    f"Invalid endpoint definition for {method.upper()} {route}: {exc}"
                ) from exc

    return endpoints
