"""Capability-based model routing."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from arg.config import Settings
from arg.domain import LicenceStatus
from arg.models import Model


@dataclass
class RoutingRequirements:
    capability: str
    language: str = "hi"
    profile: str = "baseline"
    quality_profile: str = "baseline"
    data_class: str = "confidential"
    allow_fallback: bool = False
    external_provider_data_allowed: bool = False
    budget_headroom_usd: float = 100.0


@dataclass
class RoutingDecision:
    id: str
    capability: str
    selected_model_id: str
    selected_provider: str
    deployment_digest: str
    fallback_chain: list[str] = field(default_factory=list)
    rejected_candidates: list[dict] = field(default_factory=list)
    estimated_cost_usd: float = 0.0
    estimated_latency_s: float = 0.0
    quality_floor: str = "baseline"
    policy_version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RoutingService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def resolve(self, session: Session, requirements: RoutingRequirements) -> RoutingDecision:
        rejected: list[dict] = []
        candidates = list(
            session.scalars(select(Model).where(Model.capability == requirements.capability))
        )
        if not candidates:
            raise ValueError(f"no registered models for capability {requirements.capability}")

        filtered: list[Model] = []
        for model in candidates:
            if self.settings.use_mock_providers is False and model.provider == "mock":
                rejected.append({"model_id": model.id, "reason": "mock_providers_disabled"})
                continue
            if requirements.language not in (model.languages or []):
                rejected.append({"model_id": model.id, "reason": "language_not_supported"})
                continue
            if model.licence_status not in {LicenceStatus.ALLOWED.value, LicenceStatus.ALLOWED_WITH_CONDITIONS.value}:
                rejected.append({"model_id": model.id, "reason": f"licence_{model.licence_status}"})
                continue
            if self.settings.license_allowlist_strict and model.licence_status == LicenceStatus.UNCLEAR.value:
                rejected.append({"model_id": model.id, "reason": "licence_unclear"})
                continue
            if model.provider != "mock" and not requirements.external_provider_data_allowed:
                if requirements.data_class in {"confidential", "restricted"}:
                    rejected.append({"model_id": model.id, "reason": "egress_not_allowed"})
                    continue
            if model.status in {"rejected", "excluded", "deprecated"}:
                rejected.append({"model_id": model.id, "reason": f"status_{model.status}"})
                continue
            filtered.append(model)

        if not filtered:
            raise ValueError(
                f"no routable model for {requirements.capability}: "
                + "; ".join(f"{item['model_id']}={item['reason']}" for item in rejected)
            )

        # Rank mock and lowest unit cost first, but preserve premium baselines when mocks disabled.
        filtered.sort(key=lambda model: (0 if model.provider == "mock" else 1, float((model.cost_inputs or {}).get("unit_usd", 0.0))))

        selected = filtered[0]
        fallback = [model.id for model in filtered[1:]] if requirements.allow_fallback else []
        cost_inputs = selected.cost_inputs or {}
        return RoutingDecision(
            id=str(uuid.uuid4()),
            capability=requirements.capability,
            selected_model_id=selected.id,
            selected_provider=selected.provider,
            deployment_digest=selected.deployment_digest,
            fallback_chain=fallback,
            rejected_candidates=rejected,
            estimated_cost_usd=float(cost_inputs.get("unit_usd", 0.0)),
            estimated_latency_s=float(cost_inputs.get("latency_s", 0.0)),
            quality_floor=requirements.quality_profile,
        )
