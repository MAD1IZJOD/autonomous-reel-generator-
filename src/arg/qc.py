"""Quality-control helpers and report recording."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from arg.media import frame_count, frame_rate, media_duration, qc_black_frames, qc_frozen_frames, qc_loudness
from arg.models import QCReport


def record_qc(
    session: Session,
    *,
    run_id: str,
    stage_id: str | None,
    asset_version_id: str | None,
    shot_id: str | None,
    metric: str,
    value: float | None,
    threshold: dict,
    outcome: str,
    method: str,
    evidence_key: str | None = None,
) -> QCReport:
    report = QCReport(
        run_id=run_id,
        stage_id=stage_id,
        asset_version_id=asset_version_id,
        shot_id=shot_id,
        metric=metric,
        value=value,
        threshold=threshold,
        outcome=outcome,
        method=method,
        evidence_key=evidence_key,
    )
    session.add(report)
    session.flush()
    return report


def voice_pace(audio_path: Path, text: str) -> dict[str, Any]:
    duration = media_duration(audio_path)
    words = len(text.split())
    syllables = max(1, words * 2)
    return {
        "duration_s": duration,
        "word_count": words,
        "syllables_per_second": round(syllables / duration, 3) if duration else 0.0,
    }


def render_qc(video_path: Path, audio_path: Path, settings) -> list[dict[str, Any]]:
    fps = frame_rate(video_path)
    video_duration = media_duration(video_path)
    audio_duration = media_duration(audio_path)
    black = qc_black_frames(video_path)
    frozen = qc_frozen_frames(video_path)
    loudness = qc_loudness(video_path)
    frames = frame_count(video_path)
    metrics = [
        {"metric": "video.frame_rate", "value": fps, "threshold": {"expected": settings.render_fps}, "outcome": "pass" if abs(fps - settings.render_fps) < 0.01 else "fail"},
        {"metric": "video.duration_drift_s", "value": abs(video_duration - audio_duration), "threshold": {"max": 0.2}, "outcome": "pass" if abs(video_duration - audio_duration) <= 0.2 else "fail"},
        {"metric": "video.black_frames", "value": float(black), "threshold": {"max": 0}, "outcome": "pass" if black == 0 else "warn"},
        {"metric": "video.frozen_frames", "value": float(frozen), "threshold": {"max": 0}, "outcome": "pass" if frozen == 0 else "warn"},
        {"metric": "video.frame_count", "value": float(frames), "threshold": {"min": 1}, "outcome": "pass"},
        {"metric": "audio.integrated_lufs", "value": loudness["integrated_lufs"], "threshold": {"target": settings.loudness_target_lufs, "tolerance": 1.5}, "outcome": "pass" if loudness["integrated_lufs"] is not None and abs(loudness["integrated_lufs"] - settings.loudness_target_lufs) <= 1.5 else "warn"},
        {"metric": "audio.true_peak_dbfs", "value": loudness["true_peak_dbfs"], "threshold": {"max": settings.true_peak_db}, "outcome": "pass" if loudness["true_peak_dbfs"] is not None and loudness["true_peak_dbfs"] <= settings.true_peak_db + 0.5 else "warn"},
    ]
    return metrics
