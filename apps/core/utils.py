"""Shared helper functions."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest


def compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of ``data`` without keys whose values are ``None``."""
    return {key: value for key, value in data.items() if value is not None}


def get_client_ip(request: HttpRequest) -> str | None:
    """Best-effort client IP from ``request`` (honors ``X-Forwarded-For`` when present)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR")
