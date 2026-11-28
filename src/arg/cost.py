"""Cost ledger and spend guardrails."""

from __future__ import annotations

from sqlalchemy.orm import Session

from arg.models import CostRecord


class CostService:
    def __init__(self, daily_budget_usd: float = 5.0):
        self.daily_budget_usd = daily_budget_usd

    def record(
        self,
        session: Session,
        *,
        run_id: str,
        stage_id: str | None,
        shot_id: str | None,
        provider: str,
        model_id: str | None,
        kind: str,
        estimated_usd: float,
        actual_usd: float,
        units: float,
        unit_name: str,
        meta: dict | None = None,
    ) -> CostRecord:
        entry = CostRecord(
            run_id=run_id,
            stage_id=stage_id,
            shot_id=shot_id,
            provider=provider,
            model_id=model_id,
            kind=kind,
            estimated_usd=estimated_usd,
            actual_usd=actual_usd,
            units=units,
            unit_name=unit_name,
            meta=meta or {},
        )
        session.add(entry)
        session.flush()
        return entry

    def run_total(self, session: Session, run_id: str) -> float:
        entries = session.query(CostRecord).filter(CostRecord.run_id == run_id).all()
        return round(sum(entry.actual_usd for entry in entries), 6)

    def check_budget(self, session: Session, estimated_usd: float) -> None:
        total = session.query(CostRecord).all()
        spent = sum(entry.actual_usd for entry in total)
        if spent + estimated_usd > self.daily_budget_usd:
            raise ValueError(
                f"budget exceeded: spent {spent:.4f} + estimated {estimated_usd:.4f} "
                f"> cap {self.daily_budget_usd:.4f}"
            )
