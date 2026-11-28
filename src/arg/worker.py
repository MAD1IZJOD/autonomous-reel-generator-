"""Worker loop for claiming and executing durable jobs."""

from __future__ import annotations

import time
import uuid
from typing import Callable

from arg.config import Settings
from arg.jobs import JobEngine
from arg.pipeline import PipelineService


class Worker:
    def __init__(
        self,
        settings: Settings,
        job_engine: JobEngine,
        pipeline: PipelineService,
        worker_id: str | None = None,
    ):
        self.settings = settings
        self.job_engine = job_engine
        self.pipeline = pipeline
        self.worker_id = worker_id or f"{settings.worker_role}-{uuid.uuid4().hex[:8]}"

    def run_once(self) -> bool:
        claimed = self.job_engine.claim(self.worker_id, ["preflight", "plan", "voice", "keyframe", "motion", "presenter", "graphics", "render", "qc", "export"])
        if claimed is None:
            return False
        self.pipeline.handle_job(claimed)
        return True

    def run_until_idle(self, max_iterations: int = 1000) -> int:
        processed = 0
        for _ in range(max_iterations):
            if not self.run_once():
                break
            processed += 1
        return processed

    def run_forever(self, stop: Callable[[], bool] | None = None) -> None:
        while not (stop and stop()):
            if not self.run_once():
                time.sleep(self.settings.job_poll_seconds)


def run_pipeline_to_completion(worker: Worker, is_terminal: Callable[[], bool], max_iterations: int = 10000) -> int:
    processed = 0
    for _ in range(max_iterations):
        if is_terminal():
            return processed
        if not worker.run_once():
            time.sleep(worker.settings.job_poll_seconds)
            continue
        processed += 1
    raise RuntimeError("worker did not reach a terminal state")
