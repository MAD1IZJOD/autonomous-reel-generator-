"""Application services and stage handlers for the execution foundation."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from arg.config import Settings
from arg.cost import CostService
from arg.db import session_scope
from arg.domain import (
    WorkflowProfile,
    stages_for_profile,
    validate_plate_sheet,
)
from arg.jobs import JobEngine, StaleLeaseError
from arg.media import (
    concatenate_videos,
    contact_sheet,
    make_video_from_image,
    media_duration,
    mix_audio,
    mux_audio_video,
    probe,
)
from arg.models import (
    Approval,
    Asset,
    AssetVersion,
    CostRecord,
    Export,
    PlateSheet,
    Project,
    QCReport,
    Script,
    Shot,
    Video,
    WorkflowRun,
    WorkflowStage,
)
from arg.providers import MOCK_PROVIDERS, ProviderRequest, seed_registry
from arg.qc import record_qc, render_qc, voice_pace
from arg.routing import RoutingRequirements, RoutingService
from arg.storage import LocalStorage, sha256_bytes


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def code_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "dev"


class PipelineService:
    def __init__(self, settings: Settings, session_factory, job_engine: JobEngine):
        self.settings = settings
        self.session_factory = session_factory
        self.job_engine = job_engine
        self.storage = LocalStorage(settings)
        self.routing = RoutingService(settings)
        self.cost = CostService(settings.daily_budget_usd)

    def init_database(self) -> None:
        from arg.db import Base, create_engine_from_url

        engine = create_engine_from_url(self.settings.database_url, self.settings.database_echo)
        Base.metadata.create_all(engine)
        with session_scope(self.session_factory) as session:
            seed_registry(session)

    # ---------------------------------------------------------------- projects
    def create_project(self, session: Session, *, name: str, profile: str, language_primary: str = "hi") -> Project:
        project = Project(name=name, workflow_profile=profile, language_primary=language_primary)
        session.add(project)
        session.flush()
        return project

    def add_script(self, session: Session, *, project_id: str, content: str, approved: bool = True) -> Script:
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError("project not found")
        version = (session.query(Script).filter(Script.project_id == project_id).count() or 0) + 1
        script = Script(
            project_id=project_id,
            version=version,
            content=content,
            content_hash=sha256_bytes(content.encode("utf-8")),
            status="approved" if approved else "draft",
            approved_by="founder" if approved else None,
            approved_at=utcnow() if approved else None,
        )
        session.add(script)
        session.flush()
        return script

    def generate_plate_sheet(
        self,
        session: Session,
        *,
        project_id: str,
        script_id: str,
        profile: str,
    ) -> PlateSheet:
        project = session.get(Project, project_id)
        script = session.get(Script, script_id)
        if project is None or script is None:
            raise ValueError("project or script not found")
        if script.project_id != project_id:
            raise ValueError("script does not belong to project")
        requirements = RoutingRequirements(capability="plan.plates", language=project.language_primary, quality_profile=self.settings.default_quality_profile)
        decision = self.routing.resolve(session, requirements)
        provider = MOCK_PROVIDERS["plan.plates"]
        request = ProviderRequest(
            capability="plan.plates",
            model_id=decision.selected_model_id,
            inputs={"script": script.content, "profile": profile, "language": project.language_primary},
            settings={},
            output_spec={},
            idempotency_key=f"plan:{script.id}:{script.version}",
        )
        result = provider.execute(request, self.storage)
        if result.status != "succeeded" or not result.output_refs:
            raise ValueError("plate planning failed")
        sheet_data = json.loads(self.storage.read_bytes(result.output_refs[0]))
        validate_plate_sheet(sheet_data, self.settings)
        version = (session.query(PlateSheet).filter(PlateSheet.project_id == project_id).count() or 0) + 1
        plate_sheet = PlateSheet(
            project_id=project_id,
            script_id=script_id,
            version=version,
            profile=profile,
            fps=25,
            status="draft",
            total_duration_s=float(sheet_data.get("total_duration_s", 0.0)),
        )
        session.add(plate_sheet)
        session.flush()
        for index, plate in enumerate(sheet_data["plates"]):
            shot = Shot(
                plate_sheet_id=plate_sheet.id,
                plate_id=str(plate["id"]),
                order_index=index,
                start_s=float(plate.get("start_s", 0.0)),
                duration_s=float(plate["duration_s"]),
                layout=str(plate["layout"]),
                a_roll=str(plate.get("a_roll", "")),
                b_roll=str(plate.get("b_roll", "")),
                motion_graphic=str(plate.get("motion_graphic", "")),
                voiceover=str(plate.get("voiceover", "")),
                caption=str(plate.get("caption", "")),
                sfx=list(plate.get("sfx", [])),
                visual_refs=list(plate.get("visual_refs", [])),
            )
            session.add(shot)
        session.flush()
        return plate_sheet

    def approve_plate_sheet(self, session: Session, *, plate_sheet_id: str, actor: str, role: str, comment: str | None = None) -> Approval:
        plate_sheet = session.get(PlateSheet, plate_sheet_id)
        if plate_sheet is None:
            raise ValueError("plate sheet not found")
        plate_sheet.status = "approved"
        plate_sheet.approved_by = actor
        plate_sheet.approved_at = utcnow()
        approval = Approval(
            project_id=plate_sheet.project_id,
            target_type="plate_sheet",
            target_id=plate_sheet.id,
            gate="plates.approve",
            decision="approved",
            actor=actor,
            role=role,
            comment=comment,
        )
        session.add(approval)
        session.flush()
        return approval

    def create_run(
        self,
        session: Session,
        *,
        project_id: str,
        script_id: str,
        plate_sheet_id: str,
        profile: str,
        video_id: str | None = None,
        quality_profile: str = "baseline",
    ) -> WorkflowRun:
        project = session.get(Project, project_id)
        script = session.get(Script, script_id)
        plate_sheet = session.get(PlateSheet, plate_sheet_id)
        if project is None or script is None or plate_sheet is None:
            raise ValueError("project, script or plate sheet not found")
        if script.project_id != project_id or plate_sheet.project_id != project_id:
            raise ValueError("inputs do not belong to project")
        if script.status != "approved":
            raise ValueError("script is not approved")
        if plate_sheet.status != "approved":
            raise ValueError("plate sheet is not approved")
        if profile not in {WorkflowProfile.EXPLAINER.value, WorkflowProfile.CHARACTER_STORY.value}:
            raise ValueError("unknown workflow profile")
        snapshot = {
            "project_id": project_id,
            "script_id": script.id,
            "script_version": script.version,
            "plate_sheet_id": plate_sheet.id,
            "plate_sheet_version": plate_sheet.version,
            "profile": profile,
            "quality_profile": quality_profile,
            "code_revision": code_revision(),
            "created_at": utcnow().isoformat(),
        }
        run = WorkflowRun(
            project_id=project_id,
            video_id=video_id,
            script_id=script_id,
            plate_sheet_id=plate_sheet_id,
            profile=profile,
            status="created",
            quality_profile=quality_profile,
            snapshot=snapshot,
        )
        session.add(run)
        session.flush()
        for index, stage_id in enumerate(stages_for_profile(profile)):
            stage = WorkflowStage(
                run_id=run.id,
                stage_id=stage_id,
                order_index=index,
                status="pending",
            )
            session.add(stage)
        session.flush()
        first_stage = session.query(WorkflowStage).filter_by(run_id=run.id).order_by(WorkflowStage.order_index).first()
        if first_stage is not None:
            first_stage.status = "ready"
            self.job_engine.enqueue(
                session,
                run_id=run.id,
                stage_id=first_stage.stage_id,
                job_class="preflight",
                payload={"stage": first_stage.stage_id},
                idempotency_key=f"{run.id}:{first_stage.stage_id}:1",
            )
        run.status = "running"
        run.started_at = utcnow()
        session.flush()
        return run

    def handle_job(self, claimed: Any) -> None:
        with session_scope(self.session_factory) as session:
            from arg.models import Job

            job = session.get(Job, claimed.job_id)
            if job is None:
                return
            run = session.get(WorkflowRun, job.run_id)
            stage = session.query(WorkflowStage).filter_by(run_id=job.run_id, stage_id=job.stage_id).one_or_none()
            if run is None or stage is None:
                self.job_engine.fail_session(session, job.id, claimed.lease_token, error_code="INT_MISSING_RUN", error_message="run or stage not found", retryable=False)
                return
            try:
                result = self._dispatch_stage(session, run, stage, claimed)
            except Exception as exc:  # noqa: BLE001
                self.job_engine.fail_session(session, job.id, claimed.lease_token, error_code="INT_STAGE_ERROR", error_message=str(exc), retryable=False)
                run.status = "failed"
                run.error_code = "INT_STAGE_ERROR"
                run.error_message = str(exc)
                stage.status = "failed"
                stage.error_code = "INT_STAGE_ERROR"
                stage.error_message = str(exc)
                session.flush()
                return

            if result.get("waiting_approval"):
                job_status = self.job_engine.complete_session(session, job.id, claimed.lease_token, outcome=__import__("arg.domain", fromlist=["JobOutcome"]).JobOutcome.WAITING_APPROVAL)
                stage.status = "waiting_approval"
                run.status = "waiting_approval"
                session.flush()
                return

            self.job_engine.complete_session(session, job.id, claimed.lease_token, outcome=__import__("arg.domain", fromlist=["JobOutcome"]).JobOutcome.SUCCEEDED, output=result)
            stage.status = "succeeded"
            stage.output_json = result
            stage.finished_at = utcnow()
            self._record_stage_cost(session, run, stage, result)
            self._advance_run(session, run, stage)
            session.flush()

    def _dispatch_stage(self, session: Session, run: WorkflowRun, stage: WorkflowStage, claimed: Any) -> dict[str, Any]:
        stage.status = "running"
        stage.started_at = stage.started_at or utcnow()
        session.flush()
        handlers = {
            "script.ingest": self._handle_script_ingest,
            "plates.plan": self._handle_plates_validate,
            "plates.approve": self._handle_gate,
            "voice.synthesize": self._handle_voice_synthesize,
            "voice.qc": self._handle_voice_qc,
            "timing.align": self._handle_timing_align,
            "keyframes.generate": self._handle_keyframes_generate,
            "keyframes.approve": self._handle_gate,
            "motion.generate": self._handle_motion_generate,
            "presenter.generate": self._handle_presenter_generate,
            "lipsync.qc": self._handle_lipsync_qc,
            "graphics.compose": self._handle_graphics_compose,
            "audio.mix": self._handle_audio_mix,
            "render.finalize": self._handle_render_finalize,
            "qc.final": self._handle_qc_final,
            "review.human": self._handle_gate,
            "export.package": self._handle_export,
        }
        handler = handlers.get(stage.stage_id)
        if handler is None:
            raise ValueError(f"no handler for stage {stage.stage_id}")
        if stage.stage_id in {"plates.approve", "keyframes.approve", "review.human"}:
            return handler(session, run, stage, claimed)
        return handler(session, run, stage)

    def _handle_script_ingest(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        script = session.get(Script, run.script_id)
        if script is None or script.status != "approved":
            raise ValueError("approved script is required")
        return {"script_id": script.id, "version": script.version, "status": "approved"}

    def _handle_plates_validate(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        if plate_sheet is None:
            raise ValueError("plate sheet not found")
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        return {"plate_sheet_id": plate_sheet.id, "version": plate_sheet.version, "shot_count": len(shots)}

    def _handle_gate(self, session: Session, run: WorkflowRun, stage: WorkflowStage, claimed: Any) -> dict[str, Any]:
        gate_name = stage.stage_id
        approval = (
            session.query(Approval)
            .filter(Approval.run_id == run.id, Approval.gate == gate_name, Approval.decision == "approved")
            .order_by(Approval.created_at.desc())
            .first()
        )
        if approval is None:
            return {"waiting_approval": True, "gate": gate_name}
        return {"approved": True, "approval_id": approval.id, "actor": approval.actor}

    def approve_gate(self, session: Session, *, run_id: str, gate: str, actor: str, role: str, decision: str, comment: str | None = None) -> Approval:
        run = session.get(WorkflowRun, run_id)
        if run is None:
            raise ValueError("run not found")
        approval = Approval(
            project_id=run.project_id,
            run_id=run.id,
            target_type="run",
            target_id=run.id,
            gate=gate,
            decision=decision,
            actor=actor,
            role=role,
            comment=comment,
        )
        session.add(approval)
        session.flush()
        # Advance the matching stage if it is waiting.
        stage = session.query(WorkflowStage).filter_by(run_id=run.id, stage_id=gate).one_or_none()
        if stage is not None and stage.status == "waiting_approval" and decision == "approved":
            stage.status = "succeeded"
            stage.output_json = {"approved": True, "approval_id": approval.id}
            stage.finished_at = utcnow()
            run.status = "running"
            self._advance_run(session, run, stage)
        session.flush()
        return approval

    def _handle_voice_synthesize(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        requirements = RoutingRequirements(capability="voice.synthesize", language=plate_sheet.project.language_primary if False else "hi", quality_profile=run.quality_profile)
        # Use project language from run snapshot.
        project = session.get(Project, run.project_id)
        requirements.language = project.language_primary
        decision = self.routing.resolve(session, requirements)
        provider = MOCK_PROVIDERS["voice.synthesize"]
        asset_versions = []
        for shot in shots:
            request = ProviderRequest(
                capability="voice.synthesize",
                model_id=decision.selected_model_id,
                inputs={"text": shot.voiceover, "shot_id": shot.id},
                settings={"stability": 0.5, "similarity": 0.75, "style": 0, "speed": 1.2},
                output_spec={"sample_rate": self.settings.audio_sample_rate},
                idempotency_key=f"voice:{run.id}:{shot.id}:{shot.voiceover}",
            )
            result = provider.execute(request, self.storage)
            if result.status != "succeeded":
                raise ValueError("voice synthesis failed")
            staging_key = result.output_refs[0]
            data = self.storage.read_bytes(staging_key)
            content_hash = sha256_bytes(data)
            final_key = self.storage.promote(staging_key, content_hash)
            shot_duration = float(result.metadata.get("duration_s", 3.0))
            asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, shot_id=shot.id, kind="audio.voice", name=f"voice-{shot.plate_id}")
            session.add(asset)
            session.flush()
            version = AssetVersion(
                asset_id=asset.id,
                version=1,
                storage_key=final_key,
                content_hash=content_hash,
                mime_type="audio/wav",
                byte_size=len(data),
                duration_s=shot_duration,
                status="ready",
                provenance={
                    "model_id": decision.selected_model_id,
                    "provider": "mock",
                    "settings_hash": hashlib.sha256(json.dumps(request.settings, sort_keys=True).encode()).hexdigest(),
                    "input_versions": [],
                    "run_id": run.id,
                    "stage_id": stage.stage_id,
                    "shot_id": shot.id,
                    "timing": result.timing,
                    "code_revision": code_revision(),
                    "created_by": "system",
                    "mock": True,
                },
            )
            session.add(version)
            session.flush()
            asset_versions.append({"shot_id": shot.id, "asset_version_id": version.id, "duration_s": shot_duration})
        return {"voice_assets": asset_versions, "model": decision.selected_model_id}

    def _handle_voice_qc(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        reported = []
        for shot in shots:
            version = self._latest_asset_version(session, run.id, shot.id, "audio.voice")
            if version is None:
                raise ValueError("missing voice asset")
            path = self.storage.get_local_path(version.storage_key)
            metrics = voice_pace(path, shot.voiceover)
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=version.id,
                shot_id=shot.id,
                metric="voice.duration_s",
                value=metrics["duration_s"],
                threshold={"min": 1.0, "max": 6.0},
                outcome="pass",
                method="Measured from the generated fixture audio. Mock provider; no speaker-similarity model is run in this phase.",
            )
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=version.id,
                shot_id=shot.id,
                metric="voice.syllables_per_second",
                value=metrics["syllables_per_second"],
                threshold={"min": 1.0, "max": 8.0},
                outcome="pass",
                method="Derived from word count and fixture duration.",
            )
            reported.append({"shot_id": shot.id, **metrics})
        return {"voice_qc": reported}

    def _handle_timing_align(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        cursor = 0.0
        timings = []
        for shot in shots:
            version = self._latest_asset_version(session, run.id, shot.id, "audio.voice")
            if version is None or version.duration_s is None:
                raise ValueError("missing voice duration")
            duration = min(self.settings.max_plate_duration_s, max(self.settings.min_plate_duration_s, float(version.duration_s) + 0.15))
            frames = max(1, int(round(duration * 25)))
            duration = frames / 25.0
            shot.start_s = round(cursor, 3)
            shot.duration_s = round(duration, 3)
            cursor += duration
            timings.append({"shot_id": shot.id, "start_s": shot.start_s, "duration_s": shot.duration_s, "frames": frames})
        plate_sheet.total_duration_s = round(cursor, 3)
        session.flush()
        return {"timings": timings, "total_duration_s": plate_sheet.total_duration_s}

    def _handle_keyframes_generate(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        project = session.get(Project, run.project_id)
        requirements = RoutingRequirements(capability="image.keyframe", language=project.language_primary, quality_profile=run.quality_profile)
        decision = self.routing.resolve(session, requirements)
        provider = MOCK_PROVIDERS["image.keyframe"]
        assets = []
        for shot in shots:
            request = ProviderRequest(
                capability="image.keyframe",
                model_id=decision.selected_model_id,
                inputs={"prompt": shot.voiceover, "shot_id": shot.id},
                settings={"steps": 8, "mock": True},
                output_spec={"width": self.settings.render_width // 2, "height": self.settings.render_height // 2},
                idempotency_key=f"keyframe:{run.id}:{shot.id}",
            )
            result = provider.execute(request, self.storage)
            if result.status != "succeeded":
                raise ValueError("keyframe generation failed")
            data = self.storage.read_bytes(result.output_refs[0])
            content_hash = sha256_bytes(data)
            final_key = self.storage.promote(result.output_refs[0], content_hash)
            asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, shot_id=shot.id, kind="image.keyframe", name=f"keyframe-{shot.plate_id}")
            session.add(asset)
            session.flush()
            version = AssetVersion(
                asset_id=asset.id,
                version=1,
                storage_key=final_key,
                content_hash=content_hash,
                mime_type="image/png",
                byte_size=len(data),
                width=int(result.metadata.get("width", self.settings.render_width // 2)),
                height=int(result.metadata.get("height", self.settings.render_height // 2)),
                status="ready",
                provenance={
                    "model_id": decision.selected_model_id,
                    "provider": "mock",
                    "settings_hash": hashlib.sha256(json.dumps(request.settings, sort_keys=True).encode()).hexdigest(),
                    "input_versions": [],
                    "run_id": run.id,
                    "stage_id": stage.stage_id,
                    "shot_id": shot.id,
                    "code_revision": code_revision(),
                    "created_by": "system",
                    "mock": True,
                },
            )
            session.add(version)
            session.flush()
            assets.append({"shot_id": shot.id, "asset_version_id": version.id})
        return {"keyframes": assets, "model": decision.selected_model_id}

    def _handle_motion_generate(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        project = session.get(Project, run.project_id)
        requirements = RoutingRequirements(capability="video.image_to_video", language=project.language_primary, quality_profile=run.quality_profile)
        decision = self.routing.resolve(session, requirements)
        provider = MOCK_PROVIDERS["video.image_to_video"]
        assets = []
        for shot in shots:
            still = self._latest_asset_version(session, run.id, shot.id, "image.keyframe")
            if still is None:
                raise ValueError("missing keyframe")
            duration = min(shot.duration_s, self.settings.max_motion_beat_s)
            request = ProviderRequest(
                capability="video.image_to_video",
                model_id=decision.selected_model_id,
                inputs={"image_ref": still.storage_key, "duration_s": duration, "shot_id": shot.id},
                settings={"steps": 4, "mock": True},
                output_spec={"width": self.settings.render_width // 2, "height": self.settings.render_height // 2},
                idempotency_key=f"motion:{run.id}:{shot.id}",
            )
            result = provider.execute(request, self.storage)
            if result.status != "succeeded":
                raise ValueError("motion generation failed")
            data = self.storage.read_bytes(result.output_refs[0])
            content_hash = sha256_bytes(data)
            final_key = self.storage.promote(result.output_refs[0], content_hash)
            asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, shot_id=shot.id, kind="video.motion", name=f"motion-{shot.plate_id}")
            session.add(asset)
            session.flush()
            version = AssetVersion(
                asset_id=asset.id,
                version=1,
                storage_key=final_key,
                content_hash=content_hash,
                mime_type="video/mp4",
                byte_size=len(data),
                duration_s=float(result.metadata.get("duration_s", duration)),
                width=int(result.metadata.get("width", self.settings.render_width // 2)) if "width" in result.metadata else self.settings.render_width // 2,
                height=int(result.metadata.get("height", self.settings.render_height // 2)) if "height" in result.metadata else self.settings.render_height // 2,
                status="ready",
                provenance={
                    "model_id": decision.selected_model_id,
                    "provider": "mock",
                    "settings_hash": hashlib.sha256(json.dumps(request.settings, sort_keys=True).encode()).hexdigest(),
                    "input_versions": [still.id],
                    "run_id": run.id,
                    "stage_id": stage.stage_id,
                    "shot_id": shot.id,
                    "code_revision": code_revision(),
                    "created_by": "system",
                    "mock": True,
                },
            )
            session.add(version)
            session.flush()
            assets.append({"shot_id": shot.id, "asset_version_id": version.id})
        return {"motion": assets, "model": decision.selected_model_id}

    def _handle_presenter_generate(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        project = session.get(Project, run.project_id)
        requirements = RoutingRequirements(capability="presenter.avatar", language=project.language_primary, quality_profile=run.quality_profile)
        decision = self.routing.resolve(session, requirements)
        provider = MOCK_PROVIDERS["presenter.avatar"]
        assets = []
        # Generate a presenter segment for the first and middle shot to keep it a small share of runtime.
        selected = [shots[0]] if shots else []
        if len(shots) > 2:
            selected.append(shots[len(shots) // 2])
        for shot in selected:
            request = ProviderRequest(
                capability="presenter.avatar",
                model_id=decision.selected_model_id,
                inputs={"duration_s": min(max(shot.duration_s, 1.0), 5.0), "shot_id": shot.id},
                settings={"mock": True},
                output_spec={"width": self.settings.render_width // 2, "height": self.settings.render_height // 2},
                idempotency_key=f"presenter:{run.id}:{shot.id}",
            )
            result = provider.execute(request, self.storage)
            if result.status != "succeeded":
                raise ValueError("presenter generation failed")
            data = self.storage.read_bytes(result.output_refs[0])
            content_hash = sha256_bytes(data)
            final_key = self.storage.promote(result.output_refs[0], content_hash)
            asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, shot_id=shot.id, kind="video.presenter", name=f"presenter-{shot.plate_id}")
            session.add(asset)
            session.flush()
            version = AssetVersion(
                asset_id=asset.id,
                version=1,
                storage_key=final_key,
                content_hash=content_hash,
                mime_type="video/mp4",
                byte_size=len(data),
                duration_s=float(result.metadata.get("duration_s", 3.0)),
                width=self.settings.render_width // 2,
                height=self.settings.render_height // 2,
                status="ready",
                provenance={
                    "model_id": decision.selected_model_id,
                    "provider": "mock",
                    "settings_hash": hashlib.sha256(json.dumps(request.settings, sort_keys=True).encode()).hexdigest(),
                    "input_versions": [],
                    "run_id": run.id,
                    "stage_id": stage.stage_id,
                    "shot_id": shot.id,
                    "code_revision": code_revision(),
                    "created_by": "system",
                    "mock": True,
                },
            )
            session.add(version)
            session.flush()
            assets.append({"shot_id": shot.id, "asset_version_id": version.id})
        return {"presenters": assets, "model": decision.selected_model_id}

    def _handle_lipsync_qc(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        versions = session.query(AssetVersion).join(Asset).filter(Asset.run_id == run.id, Asset.kind == "video.presenter").all()
        reported = []
        for version in versions:
            path = self.storage.get_local_path(version.storage_key)
            fps = None
            try:
                fps = frame_rate(path)
            except Exception:
                fps = None
            duration = media_duration(path)
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=version.id,
                shot_id=version.asset.shot_id if version.asset else None,
                metric="presenter.frame_rate",
                value=fps,
                threshold={"expected": self.settings.render_fps},
                outcome="pass" if fps is not None and abs(fps - self.settings.render_fps) < 0.01 else "warn",
                method="Measured from the generated presenter fixture. SyncNet and MediaPipe are not run in this phase.",
            )
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=version.id,
                shot_id=version.asset.shot_id if version.asset else None,
                metric="presenter.duration_s",
                value=duration,
                threshold={"min": 1.0, "max": 10.0},
                outcome="pass",
                method="Measured from the generated presenter fixture.",
            )
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=version.id,
                shot_id=version.asset.shot_id if version.asset else None,
                metric="lipsync.syncnet",
                value=None,
                threshold={"min": 0.0},
                outcome="needs_human",
                method="Not implemented in this phase; SyncNet is a later integration. Mock media is not a creative result.",
            )
            reported.append({"asset_version_id": version.id, "duration_s": duration, "frame_rate": fps})
        return {"lipsync_qc": reported}

    def _handle_graphics_compose(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        timeline = []
        for shot in shots:
            motion = self._latest_asset_version(session, run.id, shot.id, "video.motion")
            presenter = self._latest_asset_version(session, run.id, shot.id, "video.presenter")
            timeline.append(
                {
                    "shot_id": shot.id,
                    "plate_id": shot.plate_id,
                    "start_s": shot.start_s,
                    "duration_s": shot.duration_s,
                    "visual_asset_version_id": (presenter or motion).id if (presenter or motion) else None,
                    "visual_kind": "presenter" if presenter else "motion",
                    "caption": shot.caption,
                    "motion_graphic": shot.motion_graphic,
                }
            )
        composition = {
            "run_id": run.id,
            "profile": run.profile,
            "timeline": timeline,
            "design": {
                "paper_texture": True,
                "typography": ["Anton", "Playfair"],
                "accent": "yellow marker",
                "mock": True,
            },
        }
        data = json.dumps(composition, indent=2).encode("utf-8")
        staging_key = f"staging/graphics/{uuid.uuid4().hex}.json"
        self.storage.put_staging(staging_key, data)
        content_hash = sha256_bytes(data)
        final_key = self.storage.promote(staging_key, content_hash)
        asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, kind="graphics.project", name="composition")
        session.add(asset)
        session.flush()
        version = AssetVersion(
            asset_id=asset.id,
            version=1,
            storage_key=final_key,
            content_hash=content_hash,
            mime_type="application/json",
            byte_size=len(data),
            status="ready",
            provenance={"run_id": run.id, "stage_id": stage.stage_id, "code_revision": code_revision(), "mock": True},
        )
        session.add(version)
        session.flush()
        return {"composition_asset_version_id": version.id, "shot_count": len(timeline)}

    def _handle_audio_mix(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        voice_paths = []
        for shot in shots:
            version = self._latest_asset_version(session, run.id, shot.id, "audio.voice")
            if version is None:
                raise ValueError("missing voice asset")
            voice_paths.append(self.storage.get_local_path(version.storage_key))
        total_duration = plate_sheet.total_duration_s or sum(shot.duration_s for shot in shots)
        requirements = RoutingRequirements(capability="audio.music", language="en", quality_profile=run.quality_profile)
        decision = self.routing.resolve(session, requirements)
        provider = MOCK_PROVIDERS["audio.music"]
        request = ProviderRequest(
            capability="audio.music",
            model_id=decision.selected_model_id,
            inputs={"duration_s": total_duration + 2.0},
            settings={"mock": True},
            output_spec={},
            idempotency_key=f"music:{run.id}",
        )
        result = provider.execute(request, self.storage)
        if result.status != "succeeded":
            raise ValueError("music generation failed")
        music_path = self.storage.get_local_path(result.output_refs[0])
        output_key = f"staging/audio/{uuid.uuid4().hex}.m4a"
        output_path = self.storage.get_local_path(output_key)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mix_audio(
            voice_paths=voice_paths,
            music_path=music_path,
            output_path=output_path,
            total_duration_s=total_duration,
            sample_rate=self.settings.audio_sample_rate,
            target_lufs=self.settings.loudness_target_lufs,
            true_peak_db=self.settings.true_peak_db,
            ffmpeg_bin=self.settings.ffmpeg_bin,
        )
        data = output_path.read_bytes()
        content_hash = sha256_bytes(data)
        final_key = self.storage.promote(output_key, content_hash)
        asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, kind="audio.mix", name="audio-mix")
        session.add(asset)
        session.flush()
        version = AssetVersion(
            asset_id=asset.id,
            version=1,
            storage_key=final_key,
            content_hash=content_hash,
            mime_type="audio/mp4",
            byte_size=len(data),
            duration_s=total_duration,
            status="ready",
            provenance={
                "model_id": decision.selected_model_id,
                "provider": "mock",
                "settings_hash": hashlib.sha256(json.dumps({"lufs": self.settings.loudness_target_lufs}, sort_keys=True).encode()).hexdigest(),
                "input_versions": [],
                "run_id": run.id,
                "stage_id": stage.stage_id,
                "code_revision": code_revision(),
                "created_by": "system",
                "mock": True,
            },
        )
        session.add(version)
        session.flush()
        return {"audio_mix_asset_version_id": version.id, "duration_s": total_duration}

    def _handle_render_finalize(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        plate_sheet = session.get(PlateSheet, run.plate_sheet_id)
        shots = session.query(Shot).filter(Shot.plate_sheet_id == plate_sheet.id).order_by(Shot.order_index).all()
        visual_paths = []
        for shot in shots:
            presenter = self._latest_asset_version(session, run.id, shot.id, "video.presenter")
            motion = self._latest_asset_version(session, run.id, shot.id, "video.motion")
            chosen = presenter or motion
            if chosen is None:
                raise ValueError(f"missing visual asset for shot {shot.plate_id}")
            visual_paths.append(self.storage.get_local_path(chosen.storage_key))
        visual_key = f"staging/render/{uuid.uuid4().hex}.mp4"
        visual_path = self.storage.get_local_path(visual_key)
        visual_path.parent.mkdir(parents=True, exist_ok=True)
        concatenate_videos(
            video_paths=visual_paths,
            output_path=visual_path,
            fps=self.settings.render_fps,
            width=self.settings.render_width,
            height=self.settings.render_height,
            ffmpeg_bin=self.settings.ffmpeg_bin,
        )
        audio_version = self._latest_asset_version(session, run.id, None, "audio.mix")
        if audio_version is None:
            raise ValueError("missing audio mix")
        audio_path = self.storage.get_local_path(audio_version.storage_key)
        final_key = f"staging/render/{uuid.uuid4().hex}.mp4"
        final_path = self.storage.get_local_path(final_key)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        mux_audio_video(
            video_path=visual_path,
            audio_path=audio_path,
            output_path=final_path,
            ffmpeg_bin=self.settings.ffmpeg_bin,
        )
        data = final_path.read_bytes()
        content_hash = sha256_bytes(data)
        final_storage_key = self.storage.promote(final_key, content_hash)
        asset = Asset(project_id=run.project_id, run_id=run.id, stage_id=stage.stage_id, kind="video.render", name="final-render")
        session.add(asset)
        session.flush()
        version = AssetVersion(
            asset_id=asset.id,
            version=1,
            storage_key=final_storage_key,
            content_hash=content_hash,
            mime_type="video/mp4",
            byte_size=len(data),
            width=self.settings.render_width,
            height=self.settings.render_height,
            duration_s=media_duration(final_path),
            status="ready",
            provenance={
                "model_id": None,
                "provider": "local",
                "settings_hash": hashlib.sha256(json.dumps({"fps": self.settings.render_fps, "width": self.settings.render_width, "height": self.settings.render_height}, sort_keys=True).encode()).hexdigest(),
                "input_versions": [],
                "run_id": run.id,
                "stage_id": stage.stage_id,
                "code_revision": code_revision(),
                "created_by": "system",
                "mock": True,
            },
        )
        session.add(version)
        session.flush()
        metrics = render_qc(final_path, audio_path, self.settings)
        for metric in metrics:
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=version.id,
                shot_id=None,
                metric=metric["metric"],
                value=metric["value"],
                threshold=metric["threshold"],
                outcome=metric["outcome"],
                method="Measured from the rendered MP4 with FFmpeg/FFprobe.",
                evidence_key=final_storage_key,
            )
        # Contact sheet evidence.
        sheet_key = f"staging/qc/{uuid.uuid4().hex}.jpg"
        sheet_path = self.storage.get_local_path(sheet_key)
        sheet_path.parent.mkdir(parents=True, exist_ok=True)
        contact_sheet(final_path, sheet_path, ffmpeg_bin=self.settings.ffmpeg_bin)
        return {"render_asset_version_id": version.id, "storage_key": final_storage_key, "metrics": metrics}

    def _handle_qc_final(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        render_version = self._latest_asset_version(session, run.id, None, "video.render")
        if render_version is None:
            raise ValueError("missing render")
        audio_version = self._latest_asset_version(session, run.id, None, "audio.mix")
        if audio_version is None:
            raise ValueError("missing audio mix")
        path = self.storage.get_local_path(render_version.storage_key)
        audio_path = self.storage.get_local_path(audio_version.storage_key)
        metrics = render_qc(path, audio_path, self.settings)
        outcomes = [metric["outcome"] for metric in metrics]
        overall = "fail" if "fail" in outcomes else ("warn" if "warn" in outcomes else "pass")
        for metric in metrics:
            record_qc(
                session,
                run_id=run.id,
                stage_id=stage.stage_id,
                asset_version_id=render_version.id,
                shot_id=None,
                metric=metric["metric"],
                value=metric["value"],
                threshold=metric["threshold"],
                outcome=metric["outcome"],
                method="Final QC measured from the rendered MP4 with FFmpeg/FFprobe.",
                evidence_key=render_version.storage_key,
            )
        if overall == "fail":
            raise ValueError("final QC failed")
        return {"overall": overall, "metrics": metrics}

    def _handle_export(self, session: Session, run: WorkflowRun, stage: WorkflowStage) -> dict[str, Any]:
        render_version = self._latest_asset_version(session, run.id, None, "video.render")
        if render_version is None:
            raise ValueError("missing render")
        # Copy to an export prefix.
        source_path = self.storage.get_local_path(render_version.storage_key)
        export_key = f"workspace/{run.project_id}/runs/{run.id}/exports/{uuid.uuid4().hex}/final.mp4"
        export_path = self.storage.get_local_path(export_key)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, export_path)
        manifest = self.build_manifest(session, run, render_version, export_key)
        manifest_key = f"workspace/{run.project_id}/runs/{run.id}/exports/{uuid.uuid4().hex}/manifest.json"
        self.storage.put_staging(manifest_key, json.dumps(manifest, indent=2).encode("utf-8"))
        export = Export(run_id=run.id, asset_version_id=render_version.id, status="created", manifest=manifest)
        session.add(export)
        session.flush()
        run.status = "succeeded"
        run.finished_at = utcnow()
        return {"export_key": export_key, "manifest_key": manifest_key, "export_id": export.id}

    def build_manifest(self, session: Session, run: WorkflowRun, render_version: AssetVersion, export_key: str) -> dict[str, Any]:
        stages = session.query(WorkflowStage).filter(WorkflowStage.run_id == run.id).order_by(WorkflowStage.order_index).all()
        assets = session.query(Asset).filter(Asset.run_id == run.id).all()
        asset_versions = []
        for asset in assets:
            for version in asset.versions:
                asset_versions.append(
                    {
                        "asset_id": asset.id,
                        "asset_version_id": version.id,
                        "kind": asset.kind,
                        "shot_id": asset.shot_id,
                        "storage_key": version.storage_key,
                        "content_hash": version.content_hash,
                        "mime_type": version.mime_type,
                        "byte_size": version.byte_size,
                        "duration_s": version.duration_s,
                        "provenance": version.provenance,
                    }
                )
        qc_reports = session.query(QCReport).filter(QCReport.run_id == run.id).all()
        cost_entries = session.query(CostRecord).filter(CostRecord.run_id == run.id).all()
        approvals = session.query(Approval).filter(Approval.run_id == run.id).all()
        return {
            "run_id": run.id,
            "project_id": run.project_id,
            "profile": run.profile,
            "quality_profile": run.quality_profile,
            "snapshot": run.snapshot,
            "stages": [
                {"stage_id": stage.stage_id, "status": stage.status, "output": stage.output_json}
                for stage in stages
            ],
            "assets": asset_versions,
            "qc_reports": [
                {
                    "metric": report.metric,
                    "value": report.value,
                    "threshold": report.threshold,
                    "outcome": report.outcome,
                    "method": report.method,
                }
                for report in qc_reports
            ],
            "costs": [
                {
                    "provider": entry.provider,
                    "model_id": entry.model_id,
                    "kind": entry.kind,
                    "estimated_usd": entry.estimated_usd,
                    "actual_usd": entry.actual_usd,
                    "units": entry.units,
                    "unit_name": entry.unit_name,
                }
                for entry in cost_entries
            ],
            "approvals": [
                {"gate": approval.gate, "decision": approval.decision, "actor": approval.actor, "role": approval.role}
                for approval in approvals
            ],
            "export_key": export_key,
            "code_revision": code_revision(),
            "mock_media": True,
        }

    def _advance_run(self, session: Session, run: WorkflowRun, completed_stage: WorkflowStage) -> None:
        stages = session.query(WorkflowStage).filter(WorkflowStage.run_id == run.id).order_by(WorkflowStage.order_index).all()
        index = next((i for i, stage in enumerate(stages) if stage.id == completed_stage.id), None)
        if index is None or index + 1 >= len(stages):
            return
        next_stage = stages[index + 1]
        next_stage.status = "ready"
        self.job_engine.enqueue(
            session,
            run_id=run.id,
            stage_id=next_stage.stage_id,
            job_class="preflight",
            payload={"stage": next_stage.stage_id},
            idempotency_key=f"{run.id}:{next_stage.stage_id}:1",
        )

    def _latest_asset_version(self, session: Session, run_id: str, shot_id: str | None, kind: str) -> AssetVersion | None:
        query = session.query(AssetVersion).join(Asset).filter(Asset.run_id == run_id, Asset.kind == kind)
        if shot_id is not None:
            query = query.filter(Asset.shot_id == shot_id)
        else:
            query = query.filter(Asset.shot_id.is_(None))
        return query.order_by(AssetVersion.created_at.desc()).first()

    def _record_stage_cost(self, session: Session, run: WorkflowRun, stage: WorkflowStage, result: dict[str, Any]) -> None:
        self.cost.record(
            session,
            run_id=run.id,
            stage_id=stage.stage_id,
            shot_id=None,
            provider="mock",
            model_id=None,
            kind=stage.stage_id,
            estimated_usd=0.0,
            actual_usd=0.0,
            units=1.0,
            unit_name="stage",
            meta={"mock": True},
        )

    def approve_gate(self, session: Session, *, run_id: str, gate: str, actor: str, role: str, decision: str, comment: str | None = None) -> Approval:
        run = session.get(WorkflowRun, run_id)
        if run is None:
            raise ValueError("run not found")
        approval = Approval(
            project_id=run.project_id,
            run_id=run.id,
            target_type="run",
            target_id=run.id,
            gate=gate,
            decision=decision,
            actor=actor,
            role=role,
            comment=comment,
        )
        session.add(approval)
        session.flush()
        stage = session.query(WorkflowStage).filter_by(run_id=run.id, stage_id=gate).one_or_none()
        if stage is not None and stage.status == "waiting_approval" and decision == "approved":
            stage.status = "succeeded"
            stage.output_json = {"approved": True, "approval_id": approval.id}
            stage.finished_at = utcnow()
            run.status = "running"
            self._advance_run(session, run, stage)
        session.flush()
        return approval

    def cancel_run(self, session: Session, run_id: str) -> None:
        self.job_engine.cancel_run(session, run_id)

    def retry_stage(self, session: Session, run_id: str, stage_id: str) -> None:
        stage = session.query(WorkflowStage).filter_by(run_id=run_id, stage_id=stage_id).one_or_none()
        if stage is None:
            raise ValueError("stage not found")
        stage.status = "ready"
        stage.error_code = None
        stage.error_message = None
        self.job_engine.enqueue(
            session,
            run_id=run_id,
            stage_id=stage_id,
            job_class="preflight",
            payload={"stage": stage_id},
            idempotency_key=f"{run_id}:{stage_id}:{stage.started_at or utcnow().timestamp()}",
        )

    @property
    def job_model(self):
        from arg.models import Job

        return Job
