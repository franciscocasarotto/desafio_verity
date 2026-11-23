"""Casos de uso (application services) do servico de Lancamentos.

Camada de aplicacao: orquestra dominio + portas, aplica idempotencia e grava o
evento no outbox junto com a mudanca de estado. Nao conhece HTTP nem SQLite.
"""
from __future__ import annotations

from datetime import date

from shared.event_schema import LancamentoCancelado, LancamentoCriado

from ..domain.models import (
    ConflictError,
    Lancamento,
    ResultadoIdempotente,
    StatusLancamento,
    TipoLancamento,
    ValidationError,
    payload_hash,
)
from ..domain.ports import EventPublisher, LancamentoRepository

TOPIC_LANCAMENTOS = "lancamentos.v1"


class ServicoLancamentos:
    def __init__(
        self, repo: LancamentoRepository, publisher: EventPublisher
    ) -> None:
        self._repo = repo
        self._publisher = publisher

    # --- RF-01: registrar lancamento (idempotente) ------------------------
    def criar(
        self,
        *,
        merchant_id: str,
        tipo: str,
        valor_centavos: int,
        data_vencimento: str,
        descricao: str,
        idempotency_key: str | None = None,
        correlation_id: str = "-",
    ) -> ResultadoIdempotente:
        try:
            tipo_enum = TipoLancamento(tipo)
        except ValueError as exc:
            raise ValidationError(
                f"tipo invalido: {tipo} (esperado DEBITO ou CREDITO)"
            ) from exc
        venc = date.fromisoformat(data_vencimento)
        hash_entrada = payload_hash(
            merchant_id, tipo, valor_centavos, data_vencimento, descricao
        )

        if idempotency_key:
            existente = self._repo.find_by_idempotency_key(
                merchant_id, idempotency_key
            )
            if existente is not None:
                if existente.payload_hash != hash_entrada:
                    # Chave reutilizada com payload diferente -> conflito real
                    raise ConflictError(
                        "idempotency-key ja utilizada com payload diferente"
                    )
                return ResultadoIdempotente(lancamento=existente, created=False)

        lanc = Lancamento(
            merchant_id=merchant_id,
            tipo=tipo_enum,
            valor_centavos=valor_centavos,
            data_vencimento=venc,
            descricao=descricao,
            idempotency_key=idempotency_key,
            payload_hash=hash_entrada,
        )
        self._repo.add(lanc)

        evento = LancamentoCriado(
            merchant_id=merchant_id,
            correlation_id=correlation_id,
            lancamento_id=lanc.id,
            tipo=tipo_enum.value,
            valor_centavos=valor_centavos,
            data_vencimento=data_vencimento,
            descricao=descricao,
        )
        self._emitir(evento)
        return ResultadoIdempotente(lancamento=lanc, created=True)

    # --- RF-04: cancelar/estornar lancamento ------------------------------
    def cancelar(
        self,
        *,
        merchant_id: str,
        lancamento_id: str,
        motivo: str | None = None,
        correlation_id: str = "-",
    ) -> Lancamento:
        lanc = self._repo.get(lancamento_id)
        if lanc is None or lanc.merchant_id != merchant_id:
            raise ValidationError("lancamento nao encontrado")
        lanc.cancelar(motivo)
        self._repo.update(lanc)

        evento = LancamentoCancelado(
            merchant_id=merchant_id,
            correlation_id=correlation_id,
            lancamento_id=lanc.id,
            motivo=motivo,
        )
        self._emitir(evento)
        return lanc

    # --- RF-02/RF-03: consulta -------------------------------------------
    def listar(
        self,
        *,
        merchant_id: str,
        inicio: str,
        fim: str,
        status: StatusLancamento | None = None,
    ) -> list[Lancamento]:
        return list(
            self._repo.list_by_periodo(
                merchant_id,
                date.fromisoformat(inicio),
                date.fromisoformat(fim),
                status.value if status else None,
            )
        )

    def obter(self, *, merchant_id: str, lancamento_id: str) -> Lancamento | None:
        lanc = self._repo.get(lancamento_id)
        return lanc if lanc and lanc.merchant_id == merchant_id else None

    # --- outbox relay ------------------------------------------------------
    def _emitir(self, evento) -> None:
        """Persiste no outbox; publish efetivo ocorre via relay (republish)."""
        payload = evento.model_dump(mode="json")
        gravar = getattr(self._repo, "save_outbox_event", None)
        if callable(gravar):
            gravar(TOPIC_LANCAMENTOS, payload)
        else:  # repos fake sem outbox: publica direto
            self._publisher.publish(payload)

    def republish_pending(self, limit: int = 100) -> int:
        """Relay do outbox: envia eventos ainda nao publicados. Idempotente
        para o consumidor (chave de deduplicacao = event_id)."""
        fetch = getattr(self._repo, "fetch_unpublished", None)
        mark = getattr(self._repo, "mark_published", None)
        if not (callable(fetch) and callable(mark)):
            return 0
        enviados = 0
        for seq, payload in fetch(limit):
            self._publisher.publish(payload)
            mark(seq)
            enviados += 1
        return enviados
