"""Durable job engine with leases, retries and cancellation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from arg.config import Settings
from arg.db import session_scope
from arg.domain import JobOutcome, JobStatus
from arg.models import Job, JobAttempt, WorkflowRun, WorkflowStage


@dataclass
class ClaimedJob:
    job_id: str
    run_id: str
    stage_id: str
    job_class: str
    payload: dict
    lease_token: str
    attempt_number: int


class StaleLeaseError(Exception):
    pass


class JobEngine:
    def __init__(self, session_factory, settings: Settings):
        self.session_factory = session_factory
        self.settings = settings

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def enqueue(
        self,
        session: Session,
        *,
        run_id: str,
        stage_id: str,
        job_class: str,
        payload: dict,
        idempotency_key: str,
        priority: int = 100,
        max_attempts: int | None = None,
    ) -> Job:
        existing = session.query(Job).filter(Job.idempotency_key == idempotency_key).one_or_none()
        if existing is not None:
            return existing
        job = Job(
            run_id=run_id,
            stage_id=stage_id,
            job_class=job_class,
            status=JobStatus.QUEUED.value,
            priority=priority,
            payload=payload or {},
            idempotency_key=idempotency_key,
            max_attempts=max_attempts or self.settings.job_max_attempts,
            available_at=self._now(),
        )
        session.add(job)
        session.flush()
        return job

    def claim(self, worker_id: str, classes: Sequence[str], lease_seconds: int | None = None) -> ClaimedJob | None:
        lease = lease_seconds or self.settings.job_lease_seconds
        with session_scope(self.session_factory) as session:
            bind = session.get_bind()
            dialect = getattr(getattr(bind, "dialect", None), "name", "sqlite")
            query = (
                session.query(Job)
                .filter(Job.status == JobStatus.QUEUED.value)
                .filter(Job.available_at <= self._now())
                .filter(Job.job_class.in_(list(classes)))
                .order_by(Job.priority.asc(), Job.created_at.asc())
            )
            if dialect == "postgresql":
                query = query.with_for_update(skip_locked=True)
            else:
                query = query.with_for_update()
            job = query.first()
            if job is None:
                return None
            if job.cancel_requested:
                job.status = JobStatus.CANCELLED.value
                session.flush()
                return None

            lease_token = uuid.uuid4().hex
            job.status = JobStatus.RUNNING.value
            job.worker_id = worker_id
            job.lease_token = lease_token
            job.heartbeat_at = self._now()
            job.lease_expires_at = self._now() + timedelta(seconds=lease)
            job.attempts += 1
            attempt = JobAttempt(
                job_id=job.id,
                attempt_number=job.attempts,
                worker_id=worker_id,
                lease_token=lease_token,
                outcome="running",
            )
            session.add(attempt)
            session.flush()
            return ClaimedJob(
                job_id=job.id,
                run_id=job.run_id,
                stage_id=job.stage_id,
                job_class=job.job_class,
                payload=dict(job.payload or {}),
                lease_token=lease_token,
                attempt_number=job.attempts,
            )

    def heartbeat(self, job_id: str, lease_token: str, extend_seconds: int | None = None) -> None:
        extend = extend_seconds or self.settings.job_lease_seconds
        with session_scope(self.session_factory) as session:
            job = session.get(Job, job_id)
            if job is None or job.lease_token != lease_token:
                raise StaleLeaseError("unknown or stale job lease")
            if job.status not in {JobStatus.RUNNING.value, JobStatus.CLAIMED.value}:
                raise StaleLeaseError(f"job is not running: {job.status}")
            now = self._now()
            job.heartbeat_at = now
            job.lease_expires_at = now + timedelta(seconds=extend)

    def complete(
        self,
        job_id: str,
        lease_token: str,
        *,
        outcome: JobOutcome,
        output: dict | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> Job:
        with session_scope(self.session_factory) as session:
            job = session.get(Job, job_id)
            if job is None:
                raise ValueError("job not found")
            if job.lease_token != lease_token:
                raise StaleLeaseError("stale lease token")
            if job.status in {JobStatus.SUCCEEDED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value}:
                return job
            job.status = outcome.value
            if outcome == JobOutcome.SUCCEEDED:
                job.error_code = None
                job.error_message = None
            else:
                job.error_code = error_code
                job.error_message = error_message
            job.lease_token = None
            job.worker_id = None
            job.lease_expires_at = None
            attempt = (
                session.query(JobAttempt)
                .filter(JobAttempt.job_id == job_id, JobAttempt.lease_token == lease_token)
                .one_or_none()
            )
            if attempt is not None:
                attempt.outcome = outcome.value
                attempt.error_code = error_code
                attempt.detail = error_message
                attempt.finished_at = self._now()
                attempt.heartbeat_at = self._now()
            session.flush()
            return job

    def fail(
        self,
        job_id: str,
        lease_token: str,
        *,
        error_code: str,
        error_message: str,
        retryable: bool,
    ) -> Job:
        with session_scope(self.session_factory) as session:
            job = session.get(Job, job_id)
            if job is None:
                raise ValueError("job not found")
            if job.lease_token != lease_token:
                raise StaleLeaseError("stale lease token")
            attempt = (
                session.query(JobAttempt)
                .filter(JobAttempt.job_id == job_id, JobAttempt.lease_token == lease_token)
                .one_or_none()
            )
            if attempt is not None:
                attempt.outcome = JobStatus.FAILED.value
                attempt.error_code = error_code
                attempt.detail = error_message
                attempt.finished_at = self._now()
            if retryable and job.attempts < job.max_attempts:
                job.status = JobStatus.RETRYABLE.value
                job.available_at = self._now() + timedelta(seconds=min(300, 2 ** job.attempts))
                job.error_code = error_code
                job.error_message = error_message
                job.lease_token = None
                job.worker_id = None
                job.lease_expires_at = None
                # Move retryable jobs back to queued after backoff; for the first slice, queue immediately.
                job.status = JobStatus.QUEUED.value
            else:
                job.status = JobStatus.FAILED.value
                job.error_code = error_code
                job.error_message = error_message
                job.lease_token = None
                job.worker_id = None
                job.lease_expires_at = None
            session.flush()
            return job

    def cancel_run(self, session: Session, run_id: str) -> None:
        run = session.get(WorkflowRun, run_id)
        if run is None:
            raise ValueError("run not found")
        run.status = "cancelled"
        for job in session.query(Job).filter(Job.run_id == run_id).all():
            if job.status in {JobStatus.QUEUED.value, JobStatus.RETRYABLE.value}:
                job.status = JobStatus.CANCELLED.value
            job.cancel_requested = True
        for stage in session.query(WorkflowStage).filter(WorkflowStage.run_id == run_id).all():
            if stage.status not in {"succeeded", "failed", "cancelled"}:
                stage.status = "cancelled"
                stage.finished_at = self._now()
        session.flush()

    def reclaim_lost(self) -> int:
        reclaimed = 0
        with session_scope(self.session_factory) as session:
            now = self._now()
            jobs = (
                session.query(Job)
                .filter(Job.status == JobStatus.RUNNING.value)
                .filter(Job.lease_expires_at.is_not(None))
                .filter(Job.lease_expires_at < now)
                .all()
            )
            for job in jobs:
                job.status = JobStatus.LOST.value
                reclaimed += 1
            session.flush()
            for job in jobs:
                job.status = JobStatus.QUEUED.value
                job.lease_token = None
                job.worker_id = None
                job.lease_expires_at = None
                job.available_at = now
            session.flush()
        return reclaimed
