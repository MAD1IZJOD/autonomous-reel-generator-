"""Pure domain rules for workflow profiles, stages and validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from arg.config import Settings


class WorkflowProfile(str, Enum):
    EXPLAINER = "explainer"
    CHARACTER_STORY = "character_story"


class RunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class JobStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    CLAIMED = "claimed"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    RETRYABLE = "retryable"
    LOST = "lost"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssetStatus(str, Enum):
    CREATED = "created"
    STAGING = "staging"
    READY = "ready"
    QC_RUNNING = "qc_running"
    QC_COMPLETE = "qc_complete"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    EXPORTED = "exported"
    DELETED = "deleted"


class JobOutcome(str, Enum):
    SUCCEEDED = "succeeded"
    RETRYABLE = "retryable"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"


class QualityOutcome(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    NEEDS_HUMAN = "needs_human"


class LicenceStatus(str, Enum):
    ALLOWED = "allowed"
    ALLOWED_WITH_CONDITIONS = "allowed_with_conditions"
    RESEARCH_ONLY = "research_only"
    UNCLEAR = "unclear"
    REJECTED = "rejected"


class ModelQualityStatus(str, Enum):
    TESTED = "tested"
    REJECTED = "rejected"
    PROPOSED = "proposed"
    UNTESTED = "untested"
    EXCLUDED = "excluded"
    DEPRECATED = "deprecated"


EXPLAINER_STAGES = [
    "script.ingest",
    "plates.plan",
    "plates.approve",
    "voice.synthesize",
    "voice.qc",
    "timing.align",
    "keyframes.generate",
    "motion.generate",
    "presenter.generate",
    "lipsync.qc",
    "graphics.compose",
    "audio.mix",
    "render.finalize",
    "qc.final",
    "review.human",
    "export.package",
]

CHARACTER_STORY_STAGES = [
    "script.ingest",
    "plates.plan",
    "plates.approve",
    "keyframes.generate",
    "keyframes.approve",
    "voice.synthesize",
    "voice.qc",
    "timing.align",
    "motion.generate",
    "presenter.generate",
    "lipsync.qc",
    "graphics.compose",
    "audio.mix",
    "render.finalize",
    "qc.final",
    "review.human",
    "export.package",
]

STAGE_JOB_CLASS = {
    "script.ingest": "preflight",
    "plates.plan": "plan",
    "plates.approve": "plan",
    "voice.synthesize": "voice",
    "voice.qc": "qc",
    "timing.align": "plan",
    "keyframes.generate": "keyframe",
    "keyframes.approve": "keyframe",
    "motion.generate": "motion",
    "presenter.generate": "presenter",
    "lipsync.qc": "qc",
    "graphics.compose": "graphics",
    "audio.mix": "render",
    "render.finalize": "render",
    "qc.final": "qc",
    "review.human": "export",
    "export.package": "export",
}

GATES = {
    "plates.approve": "plates.approve",
    "keyframes.approve": "keyframes.approve",
    "review.human": "review.human",
}


@dataclass(frozen=True)
class PlateInput:
    plate_id: str
    duration_s: float
    layout: str
    voiceover: str
    a_roll: str = ""
    b_roll: str = ""
    motion_graphic: str = ""
    caption: str = ""


def stages_for_profile(profile: WorkflowProfile | str) -> list[str]:
    normalized = profile.value if isinstance(profile, WorkflowProfile) else str(profile)
    if normalized == WorkflowProfile.EXPLAINER.value:
        return list(EXPLAINER_STAGES)
    if normalized == WorkflowProfile.CHARACTER_STORY.value:
        return list(CHARACTER_STORY_STAGES)
    raise ValueError(f"unknown workflow profile: {profile}")


def validate_plate(plate: dict, settings: Settings) -> None:
    required = ("id", "duration_s", "layout", "voiceover")
    for field in required:
        if field not in plate:
            raise ValueError(f"plate is missing required field: {field}")
    plate_id = str(plate["id"]).strip()
    if not plate_id:
        raise ValueError("plate id must not be empty")
    duration = float(plate["duration_s"])
    if duration < settings.min_plate_duration_s or duration > settings.max_plate_duration_s:
        raise ValueError(
            f"plate {plate_id} duration {duration:.2f}s is outside "
            f"{settings.min_plate_duration_s:.1f}-{settings.max_plate_duration_s:.1f}s"
        )
    layout = str(plate["layout"]).strip()
    if not layout:
        raise ValueError(f"plate {plate_id} has an empty layout")
    voiceover = str(plate["voiceover"]).strip()
    if not voiceover and not bool(plate.get("silent")):
        raise ValueError(f"plate {plate_id} has no voiceover and is not marked silent")
    if "caption" in plate and plate["caption"] is None:
        raise ValueError(f"plate {plate_id} has a null caption")
    if "sfx" in plate and not isinstance(plate["sfx"], list):
        raise ValueError(f"plate {plate_id} sfx must be a list")
    if "visual_refs" in plate and not isinstance(plate["visual_refs"], list):
        raise ValueError(f"plate {plate_id} visual_refs must be a list")


def validate_plate_sheet(sheet: dict, settings: Settings) -> None:
    if not isinstance(sheet, dict):
        raise ValueError("plate sheet must be an object")
    if int(sheet.get("schema_version", 0)) < 1:
        raise ValueError("plate sheet schema_version must be at least 1")
    if int(sheet.get("fps", 0)) != 25:
        raise ValueError("plate sheet must declare 25 FPS")
    plates = sheet.get("plates")
    if not isinstance(plates, list) or not plates:
        raise ValueError("plate sheet must contain at least one plate")
    seen: set[str] = set()
    total = 0.0
    for plate in plates:
        if not isinstance(plate, dict):
            raise ValueError("each plate must be an object")
        validate_plate(plate, settings)
        plate_id = str(plate["id"])
        if plate_id in seen:
            raise ValueError(f"duplicate plate id: {plate_id}")
        seen.add(plate_id)
        total += float(plate["duration_s"])
    if abs(total - float(sheet.get("total_duration_s", total))) > 0.01:
        raise ValueError("plate sheet total_duration_s does not match plate durations")


def terminal_job_statuses() -> set[str]:
    return {JobStatus.SUCCEEDED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value}


def is_terminal_job_status(status: str) -> bool:
    return status in terminal_job_statuses()


def capability_for_stage(stage_id: str) -> str | None:
    mapping = {
        "plates.plan": "plan.plates",
        "voice.synthesize": "voice.synthesize",
        "keyframes.generate": "image.keyframe",
        "motion.generate": "video.image_to_video",
        "presenter.generate": "presenter.avatar",
        "lipsync.qc": "qc.lipsync",
        "graphics.compose": "graphics.compose",
        "audio.mix": "audio.music",
        "qc.final": "qc.final",
    }
    return mapping.get(stage_id)


def ensure_iterable(value: Iterable) -> list:
    return list(value)
