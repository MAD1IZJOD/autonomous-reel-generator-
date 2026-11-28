"""Validated application configuration."""

from __future__ import annotations

import shutil
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "autonomous-reel-generator"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "info"

    database_url: str = "sqlite:///./var/arg.db"
    database_echo: bool = False

    storage_root: Path = Path("var/storage")
    media_root: Path = Path("var/media")

    ffmpeg_bin: str = "ffmpeg"
    ffprobe_bin: str = "ffprobe"
    render_width: int = Field(default=1080, ge=64)
    render_height: int = Field(default=1920, ge=64)
    render_fps: int = Field(default=25, ge=1, le=60)
    audio_sample_rate: int = Field(default=48000, ge=8000)
    loudness_target_lufs: float = -14.0
    true_peak_db: float = -1.0

    job_lease_seconds: int = Field(default=120, ge=5)
    job_max_attempts: int = Field(default=3, ge=1)
    job_poll_seconds: float = Field(default=0.25, ge=0.01)

    spend_cap_usd: float = Field(default=5.0, ge=0.0)
    daily_budget_usd: float = Field(default=5.0, ge=0.0)
    require_cost_approval_above_usd: float = Field(default=0.0, ge=0.0)

    use_mock_providers: bool = True
    allow_external_provider_data: bool = False
    license_allowlist_strict: bool = True
    default_quality_profile: Literal["draft", "baseline", "high"] = "baseline"

    min_plate_duration_s: float = Field(default=2.0, gt=0)
    max_plate_duration_s: float = Field(default=6.0, gt=0)
    max_motion_beat_s: float = Field(default=2.4, gt=0)
    max_candidates_per_shot: int = Field(default=2, ge=1, le=2)

    voice_pause_threshold_s: float = 0.3
    voice_pause_target_s: float = 0.2
    voice_speed: float = 1.2
    voice_similarity_floor: float = 0.96
    whisper_cer_ceiling: float = 0.2

    seed_demo_data: bool = True
    skip_media_tool_check: bool = False

    @model_validator(mode="after")
    def validate_runtime(self) -> Settings:
        if self.min_plate_duration_s >= self.max_plate_duration_s:
            raise ValueError("min_plate_duration_s must be lower than max_plate_duration_s")
        if self.true_peak_db >= 0:
            raise ValueError("true_peak_db must be negative")
        if self.app_env == "production" and self.use_mock_providers:
            raise ValueError("mock providers cannot be enabled in production")
        if self.app_env == "production" and self.database_url.startswith("sqlite"):
            raise ValueError("production requires a PostgreSQL database URL")
        if not self.skip_media_tool_check:
            for tool in (self.ffmpeg_bin, self.ffprobe_bin):
                if shutil.which(tool) is None and not Path(tool).exists():
                    raise ValueError(f"media tool not found: {tool}")
        return self

    def ensure_directories(self) -> None:
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.media_root.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
