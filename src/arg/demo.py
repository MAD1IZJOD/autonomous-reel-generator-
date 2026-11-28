"""Command-line demonstration of the mocked explainer workflow."""

from __future__ import annotations

import time
from pathlib import Path

from arg.config import get_settings
from arg.db import create_engine_from_url, create_session_factory, session_scope
from arg.jobs import JobEngine
from arg.pipeline import PipelineService
from arg.worker import Worker


def run_demo(settings=None) -> dict:
    settings = settings or get_settings()
    settings.ensure_directories()
    engine = create_engine_from_url(settings.database_url, settings.database_echo)
    session_factory = create_session_factory(engine)
    job_engine = JobEngine(session_factory, settings)
    pipeline = PipelineService(settings, session_factory, job_engine)
    pipeline.init_database()
    worker = Worker(settings, job_engine, pipeline)

    script_text = """We do not need a coding assistant to ship a reel.
Every shot is a planned 2 to 6 second beat.
Voice timing decides the final cut.
Proof must be visible, not decorative.
"""

    with session_scope(session_factory) as session:
        project = pipeline.create_project(session, name="Phase 4 demo", profile="explainer")
        script = pipeline.add_script(session, project_id=project.id, content=script_text, approved=True)
        plate_sheet = pipeline.generate_plate_sheet(session, project_id=project.id, script_id=script.id, profile="explainer")
        pipeline.approve_plate_sheet(session, plate_sheet_id=plate_sheet.id, actor="founder", role="reviewer", comment="Approved for demo")
        run = pipeline.create_run(
            session,
            project_id=project.id,
            script_id=script.id,
            plate_sheet_id=plate_sheet.id,
            profile="explainer",
        )
        run_id = run.id

    def run_worker_until(predicate, limit: int = 10000) -> None:
        for _ in range(limit):
            if predicate():
                return
            if not worker.run_once():
                time.sleep(settings.job_poll_seconds)
                continue

    # Process until the human review gate.
    run_worker_until(lambda: _run_status(session_factory, run_id) == "waiting_approval")
    with session_scope(session_factory) as session:
        pipeline.approve_gate(session, run_id=run_id, gate="review.human", actor="founder", role="reviewer", decision="approved", comment="Demo approval")
    run_worker_until(lambda: _run_status(session_factory, run_id) == "succeeded")

    with session_scope(session_factory) as session:
        from arg.models import WorkflowRun

        run = session.get(WorkflowRun, run_id)
        assert run is not None and run.status == "succeeded"
        manifest = pipeline.build_manifest(session, run, _latest_render(session, run_id), _latest_render(session, run_id).storage_key)
    return {"run_id": run_id, "manifest": manifest}


def _run_status(session_factory, run_id: str) -> str:
    with session_scope(session_factory) as session:
        from arg.models import WorkflowRun

        run = session.get(WorkflowRun, run_id)
        return run.status if run is not None else "missing"


def _latest_render(session, run_id: str):
    from arg.models import Asset, AssetVersion

    asset = session.query(Asset).filter(Asset.run_id == run_id, Asset.kind == "video.render").order_by(Asset.created_at.desc()).first()
    assert asset is not None
    return session.query(AssetVersion).filter(AssetVersion.asset_id == asset.id).order_by(AssetVersion.created_at.desc()).first()


def main() -> None:
    result = run_demo()
    print(f"Run succeeded: {result['run_id']}")
    print(f"Export key: {result['manifest'].get('export_key')}")


if __name__ == "__main__":
    main()
