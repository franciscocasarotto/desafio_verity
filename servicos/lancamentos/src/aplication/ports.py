"""Interfaces (Ports) — contratos que a infraestrutura implementa."""
from abc import ABC, abstractmethod
from datetime import date
from typing import List
from uuid import UUID

from src.domain.models import Lancamento


class LancamentoRepository(ABC):
    @abstractmethod
    def save(self, lancamento: Lancamento) -> None: ...

    @abstractmethod
    def find_by_id(self, id: UUID) -> Lancamento | None: ...

    @abstractmethod
    def list_by_period(self, inicio: date, fim: date) -> List[Lancamento]: ...


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: dict) -> None: ...