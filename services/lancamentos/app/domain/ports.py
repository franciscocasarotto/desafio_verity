"""Portas (interfaces) de infraestrutura - Clean Architecture / Ports & Adapters.

O dominio e a aplicacao dependem apenas destas abstracoes; adaptadores
(SQLite/Postgres, outbox em memoria/Kafka) sao injetados na composicao raiz.
Isso viabiliza trocar SQLite (on-prem/dev) por Postgres/Azure SQL sem tocar
nas regras de negocio, e testar tudo com fakes in-memory.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence

from .models import Lancamento


class LancamentoRepository(ABC):
    @abstractmethod
    def add(self, lancamento: Lancamento) -> None: ...

    @abstractmethod
    def get(self, lancamento_id: str) -> Lancamento | None: ...

    @abstractmethod
    def find_by_idempotency_key(
        self, merchant_id: str, key: str
    ) -> Lancamento | None: ...

    @abstractmethod
    def update(self, lancamento: Lancamento) -> None: ...

    @abstractmethod
    def list_by_periodo(
        self, merchant_id: str, inicio: date, fim: date, status: str | None = None
    ) -> Sequence[Lancamento]: ...


class EventPublisher(ABC):
    """Publicador assincrono de eventos de dominio (outbox -> broker)."""

    @abstractmethod
    def publish(self, event_dict: dict) -> None: ...
