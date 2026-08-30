"""Dependency-free HTTP handlers for the pricing API."""

import json
from dataclasses import asdict
from typing import Any, Callable, Iterable

from .contracts import LineItem
from .quote import quote
from .rounding import SUPPORTED_CURRENCY_PRECISION


def quote_handler(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """Handle a ``POST /quote`` JSON payload."""

    try:
        raw_items = payload.get("items", [])
        items = [LineItem(item["name"], item["unit_price"], item["quantity"]) for item in raw_items]
        result = quote(
            items,
            shipping=payload.get("shipping", 0.0),
            discount_rate=payload.get("discount_rate", 0.0),
            tax_rate=payload.get("tax_rate", 0.0),
            currency=payload.get("currency", "USD"),
        )
    except (KeyError, TypeError, ValueError) as error:
        return 400, {"error": str(error)}
    return 200, asdict(result)


def rounding_rules_handler() -> tuple[int, dict[str, Any]]:
    """Handle ``GET /pricing/rounding-rules``."""

    return 200, dict(SUPPORTED_CURRENCY_PRECISION)


def route_request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    """Route an API request to its handler."""

    if method.upper() == "POST" and path == "/quote":
        return quote_handler(payload or {})
    if method.upper() == "GET" and path == "/pricing/rounding-rules":
        return rounding_rules_handler()
    return 404, {"error": "not found"}


def application(environ: dict[str, Any], start_response: Callable[..., Any]) -> Iterable[bytes]:
    """Expose the routes as a standard WSGI application."""

    try:
        size = int(environ.get("CONTENT_LENGTH") or 0)
        payload = json.loads(environ["wsgi.input"].read(size) or b"{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        status, body = 400, {"error": "invalid JSON body"}
    else:
        status, body = route_request(environ.get("REQUEST_METHOD", "GET"), environ.get("PATH_INFO", "/"), payload)
    encoded = json.dumps(body).encode("utf-8")
    reason = {200: "OK", 400: "Bad Request", 404: "Not Found"}[status]
    start_response(f"{status} {reason}", [("Content-Type", "application/json"), ("Content-Length", str(len(encoded)))])
    return [encoded]
