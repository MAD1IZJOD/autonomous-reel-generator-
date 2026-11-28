"""FastAPI application for the execution foundation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from arg.config import Settings, get_settings
from arg.db import create_engine_from_url, create_session_factory, session_scope
from arg.jobs import JobEngine
from arg.pipeline import PipelineService


class ProjectCreate(BaseModel):
    name: str
    profile: str = "explainer"
    language_primary: str = "hi"


class ScriptCreate(BaseModel):
    content: str
    approved: bool = True


class PlanCreate(BaseModel):
    script_id: str
    profile: str = "explainer"


class PlanApprove(BaseModel):
    actor: str = "founder"
    role: str = "reviewer"
    comment: str | None = None


class RunCreate(BaseModel):
    project_id: str
    script_id: str
    plate_sheet_id: str
    profile: str = "explainer"
    quality_profile: str = "baseline"


class ApprovalCreate(BaseModel):
    gate: str
    decision: str = "approved"
    actor: str = "founder"
    role: str = "reviewer"
    comment: str | None = None


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    settings.ensure_directories()
    engine = create_engine_from_url(settings.database_url, settings.database_echo)
    session_factory = create_session_factory(engine)
    job_engine = JobEngine(session_factory, settings)
    pipeline = PipelineService(settings, session_factory, job_engine)

    app = FastAPI(title="Autonomous Reel Generator", version="0.1.0")
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.job_engine = job_engine
    app.state.pipeline = pipeline
    from arg.worker import Worker

    app.state.worker = Worker(settings, job_engine, pipeline)

    @app.on_event("startup")
    def _startup() -> None:
        pipeline.init_database()

    def get_session() -> Any:
        with session_scope(session_factory) as session:
            yield session

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.app_env}

    @app.post("/v1/projects", status_code=201)
    def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
        project = pipeline.create_project(session, name=payload.name, profile=payload.profile, language_primary=payload.language_primary)
        return {"id": project.id, "name": project.name, "profile": project.workflow_profile}

    @app.get("/v1/projects/{project_id}")
    def get_project(project_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
        from arg.models import Project as ProjectModel

        project = session.get(ProjectModel, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="project not found")
        return {"id": project.id, "name": project.name, "profile": project.workflow_profile, "language_primary": project.language_primary}

    @app.post("/v1/projects/{project_id}/scripts", status_code=201)
    def add_script(project_id: str, payload: ScriptCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
        script = pipeline.add_script(session, project_id=project_id, content=payload.content, approved=payload.approved)
        return {"id": script.id, "version": script.version, "status": script.status}

    @app.post("/v1/projects/{project_id}/plans", status_code=201)
    def create_plan(project_id: str, payload: PlanCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
        plate_sheet = pipeline.generate_plate_sheet(session, project_id=project_id, script_id=payload.script_id, profile=payload.profile)
        shots = session.query(__import__("arg.models", fromlist=["Shot"]).Shot).filter_by(plate_sheet_id=plate_sheet.id).order_by(__import__("arg.models", fromlist=["Shot"]).Shot.order_index).all()
        return {
            "id": plate_sheet.id,
            "version": plate_sheet.version,
            "status": plate_sheet.status,
            "total_duration_s": plate_sheet.total_duration_s,
            "shots": [{"id": shot.id, "plate_id": shot.plate_id, "duration_s": shot.duration_s} for shot in shots],
        }

    @app.get("/v1/plans/{plan_id}")
    def get_plan(plan_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
        from arg.models import PlateSheet, Shot

        plate_sheet = session.get(PlateSheet, plan_id)
        if plate_sheet is None:
            raise HTTPException(status_code=404, detail="plan not found")
        shots = session.query(Shot).filter_by(plate_sheet_id=plate_sheet.id).order_by(Shot.order_index).all()
        return {
            "id": plate_sheet.id,
            "version": plate_sheet.version,
            "status": plate_sheet.status,
            "profile": plate_sheet.profile,
            "total_duration_s": plate_sheet.total_duration_s,
            "shots": [{"id": shot.id, "plate_id": shot.plate_id, "duration_s": shot.duration_s, "voiceover": shot.voiceover} for shot in shots],
        }

    @app.post("/v1/plans/{plan_id}/approve")
    def approve_plan(plan_id: str, payload: PlanApprove, session: Session = Depends(get_session)) -> dict[str, Any]:
        approval = pipeline.approve_plate_sheet(session, plate_sheet_id=plan_id, actor=payload.actor, role=payload.role, comment=payload.comment)
        return {"approval_id": approval.id, "gate": approval.gate, "decision": approval.decision}

    @app.post("/v1/runs", status_code=201)
    def create_run(payload: RunCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
        run = pipeline.create_run(
            session,
            project_id=payload.project_id,
            script_id=payload.script_id,
            plate_sheet_id=payload.plate_sheet_id,
            profile=payload.profile,
            quality_profile=payload.quality_profile,
        )
        return {"id": run.id, "status": run.status, "profile": run.profile}

    @app.get("/v1/runs/{run_id}")
    def get_run(run_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
        from arg.models import WorkflowRun, WorkflowStage

        run = session.get(WorkflowRun, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="run not found")
        stages = session.query(WorkflowStage).filter_by(run_id=run.id).order_by(WorkflowStage.order_index).all()
        return {
            "id": run.id,
            "status": run.status,
            "profile": run.profile,
            "error_code": run.error_code,
            "error_message": run.error_message,
            "stages": [{"stage_id": stage.stage_id, "status": stage.status, "output": stage.output_json} for stage in stages],
        }

    @app.post("/v1/runs/{run_id}/cancel")
    def cancel_run(run_id: str, session: Session = Depends(get_session)) -> dict[str, str]:
        pipeline.cancel_run(session, run_id)
        return {"status": "cancelled"}

    @app.post("/v1/runs/{run_id}/approvals")
    def approve_run(run_id: str, payload: ApprovalCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
        approval = pipeline.approve_gate(
            session,
            run_id=run_id,
            gate=payload.gate,
            actor=payload.actor,
            role=payload.role,
            decision=payload.decision,
            comment=payload.comment,
        )
        return {"approval_id": approval.id, "gate": approval.gate, "decision": approval.decision}

    @app.get("/v1/runs/{run_id}/manifest")
    def get_manifest(run_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
        from arg.models import WorkflowRun, AssetVersion, Asset

        run = session.get(WorkflowRun, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="run not found")
        render_version = None
        render_assets = session.query(Asset).filter(Asset.run_id == run.id, Asset.kind == "video.render").all()
        if render_assets:
            render_version = session.query(AssetVersion).filter(AssetVersion.asset_id == render_assets[-1].id).order_by(AssetVersion.created_at.desc()).first()
        if render_version is None:
            raise HTTPException(status_code=409, detail="render not available")
        return pipeline.build_manifest(session, run, render_version, render_version.storage_key)

    @app.post("/v1/worker/tick")
    def worker_tick() -> dict[str, bool]:
        processed = app.state.worker.run_once() if hasattr(app.state, "worker") else False
        # Lazily create a worker if one is not attached.
        if not hasattr(app.state, "worker"):
            from arg.worker import Worker

            app.state.worker = Worker(settings, job_engine, pipeline)
            processed = app.state.worker.run_once()
        return {"processed": processed}

    return app


def main() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(create_app(settings), host=settings.api_host, port=settings.api_port)


if __name__ == "__main__":
    main()
