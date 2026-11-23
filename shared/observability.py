"""Observabilidade compartilhada: logging estruturado (JSON) + correlacao.

Padrao adotado: logs estruturados em JSON com campos correlacionaveis
(correlation_id / trace_id) para consumo por Azure Monitor (Application
Insights) e Google Cloud Logging, sem alteracao de codigo por ambiente
(12-factor: configuracao via variaveis de ambiente).
"""
from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_var.get(),
        }
        extra = getattr(record, "context", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class _ServiceAdapter(logging.LoggerAdapter):
    """Injeta o nome do servico em todos os registros."""

    def process(self, msg, kwargs):  # type: ignore[override]
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("service", self.extra["service"])
        return msg, kwargs

    def log_event(self, level: int, message: str, **context: Any) -> None:
        """Log estruturado com contexto de negocio (ex.: ids, metricas)."""
        extra = {"context": context}
        extra.setdefault("service", self.extra["service"])
        self.log(level, message, extra=extra)


def configure_logging(service: str, level: str = "INFO") -> _ServiceAdapter:
    """Configura logging JSON idempotente e devolve adapter do servico."""
    root = logging.getLogger()
    if not any(getattr(h, "_json_handler", False) for h in root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        handler._json_handler = True  # type: ignore[attr-defined]
        root.handlers = [handler]
    root.setLevel(level.upper())
    return _ServiceAdapter(logging.getLogger(service), {"service": service})


def new_correlation_id(value: str | None = None) -> str:
    cid = value or str(uuid.uuid4())
    correlation_id_var.set(cid)
    return cid


def now_ms() -> float:
    return time.time() * 1000.0
