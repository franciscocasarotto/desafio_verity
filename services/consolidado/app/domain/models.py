"""Domain do servico de Consolidado Diario (Camada 1 - Core Business).

Modelo: read-model derivado por Event Sourcing leve — o saldo diario e a
projecao agregada dos eventos de lancamento. Recalculo deterministico:
mesmo conjunto de eventos => mesmo saldo (reprocessabilidade/auditoria).

Regras:
- CREDITO soma, DEBITO subtrai; cancelamento estorna (remove contribuicao).
- Deduplicacao por event_id (at-least-once -> exactly-once effect).
- Out-of-order tolerance: a projecao usa data_vencimento (competencia), nao a
  ordem de chegada; reprocessar o periodo inteiro garante consistencia final.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone


@dataclass
class ConsolidadoDiario:
    merchant_id: str
    dia: date
    total_creditos_centavos: int = 0
    total_debitos_centavos: int = 0
    qtd_lancamentos: int = 0
    atualizado_em: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def saldo_centavos(self) -> int:
        return self.total_creditos_centavos - self.total_debitos_centavos

    def aplicar_evento(self, evento: dict) -> None:
        """Projecao incremental de um evento de lancamento."""
        et = evento.get("event_type")
        if et == "LancamentoCriado":
            if evento["tipo"] == "CREDITO":
                self.total_creditos_centavos += evento["valor_centavos"]
            else:
                self.total_debitos_centavos += evento["valor_centavos"]
            self.qtd_lancamentos += 1
        elif et == "LancamentoCancelado":
            # Estorno: quem aplica o cancelamento deve informar o original via
            # `evento['_original']` (resolvido pelo projector com estado local).
            orig = evento.get("_original") or {}
            if orig.get("tipo") == "CREDITO":
                self.total_creditos_centavos -= orig.get("valor_centavos", 0)
            elif orig.get("tipo") == "DEBITO":
                self.total_debitos_centavos -= orig.get("valor_centavos", 0)
            self.qtd_lancamentos = max(0, self.qtd_lancamentos - 1)
        else:
            raise ValueError(f"evento nao suportado: {et}")
        self.atualizado_em = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "merchant_id": self.merchant_id,
            "dia": self.dia.isoformat(),
            "total_creditos_centavos": self.total_creditos_centavos,
            "total_debitos_centavos": self.total_debitos_centavos,
            "saldo_centavos": self.saldo_centavos,
            "qtd_lancamentos": self.qtd_lancamentos,
            "atualizado_em": self.atualizado_em.isoformat(),
        }


def consolidar_eventos(eventos: list[dict], merchant_id: str, dia: date) -> ConsolidadoDiario:
    """Recompute puro (funcao) a partir da corrente de eventos do dia.

    Usado no reprocessamento completo (recover/rebuild) — a mesma funcao serve
    para bootstrap historico e correcao de projeções corrompidas.
    """
    c = ConsolidadoDiario(merchant_id=merchant_id, dia=dia)
    originals: dict[str, dict] = {}
    for ev in eventos:
        if ev["event_type"] == "LancamentoCriado":
            originals[ev["lancamento_id"]] = ev
            c.aplicar_evento(ev)
        elif ev["event_type"] == "LancamentoCancelado":
            orig = originals.pop(ev["lancamento_id"], None)
            enriched = dict(ev)
            if orig:
                enriched["_original"] = orig
            c.aplicar_evento(enriched)
    return c
