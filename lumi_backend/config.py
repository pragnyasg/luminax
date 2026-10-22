"""
Configuration module for LUMI Caregiver Backend.
Loads settings from environment variables or defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LUMI_", extra="ignore")

    # Server network settings
    host: str = os.getenv("LUMI_HOST", "0.0.0.0")
    port: int = int(os.getenv("LUMI_PORT", "8000"))
    api_key: Optional[str] = os.getenv("LUMI_API_KEY", None)
    cors_origins: List[str] = ["*"]

    # Operating mode (Mock dev mode vs Real ROS 2 mode)
    dev_mode: bool = os.getenv("LUMI_DEV_MODE", "true").lower() in ("true", "1", "yes")

    # Robot identity
    robot_name: str = "LUMI Healthcare Companion"
    robot_id: str = "lumi-alpha-01"

    # File paths
    base_dir: Path = Path(__file__).resolve().parent
    data_dir: Path = Path(os.getenv("LUMI_DATA_DIR", str(base_dir / "data")))
    database_path: Path = data_dir / "lumi_caregiver.db"
    snapshots_dir: Path = data_dir / "snapshots"
    map_yaml_path: str = os.getenv(
        "LUMI_MAP_PATH",
        str(base_dir.parent / "robot_ws" / "src" / "robot_navigation" / "maps" / "sample_map.yaml"),
    )

    # Safety limits for manual teleoperation
    max_linear_speed: float = 0.35   # m/s
    max_angular_speed: float = 0.8   # rad/s
    cmd_vel_timeout_sec: float = 0.5 # Dead-man timeout in seconds

    # Health & reminder defaults
    medicine_escalation_sec: float = 60.0 # Time before unacknowledged reminder escalates
    caregiver_name: str = "Primary Caregiver"
    caregiver_phone: str = "+1-555-0199"
    emergency_contact_phone: str = "+1-555-9110"


settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.snapshots_dir.mkdir(parents=True, exist_ok=True)
