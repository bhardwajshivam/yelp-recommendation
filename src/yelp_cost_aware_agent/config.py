from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from yelp_cost_aware_agent.schemas.models import PolicyConfig


class AppConfig(BaseModel):
    app_name: str = "yelp-cost-aware-agent"
    environment: str = "local"
    data_dir: Path = Path("./data")
    duckdb_path: Path = Path("./data/yelp.duckdb")
    yelp_archive_path: Path = Path("./Yelp JSON/yelp_dataset.tar")
    vllm_base_url: str = "http://vllm:8000/v1"
    enable_prometheus_metrics: bool = True
    enable_mlflow: bool = False
    mlflow_tracking_uri: str = "http://mlflow:5000"
    mlflow_experiment_name: str = "yelp-cost-aware-agent"
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    quality_threshold: float = 0.65


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YCA_", extra="ignore")

    data_dir: Path | None = None
    duckdb_path: Path | None = None
    yelp_archive_path: Path | None = None
    vllm_base_url: str | None = None
    enable_prometheus_metrics: bool | None = None
    enable_mlflow: bool | None = None
    mlflow_tracking_uri: str | None = None
    mlflow_experiment_name: str | None = None
    config_path: Path = Path("./configs/base.yaml")


def load_config() -> AppConfig:
    settings = Settings()
    config_data: dict = {}
    if settings.config_path.exists():
        with settings.config_path.open("r", encoding="utf-8") as handle:
            config_data = yaml.safe_load(handle) or {}

    config = AppConfig.model_validate(config_data)

    if settings.data_dir is not None:
        config.data_dir = settings.data_dir
    if settings.duckdb_path is not None:
        config.duckdb_path = settings.duckdb_path
    if settings.yelp_archive_path is not None:
        config.yelp_archive_path = settings.yelp_archive_path
    if settings.vllm_base_url is not None:
        config.vllm_base_url = settings.vllm_base_url
    if settings.enable_prometheus_metrics is not None:
        config.enable_prometheus_metrics = settings.enable_prometheus_metrics
    if settings.enable_mlflow is not None:
        config.enable_mlflow = settings.enable_mlflow
    if settings.mlflow_tracking_uri is not None:
        config.mlflow_tracking_uri = settings.mlflow_tracking_uri
    if settings.mlflow_experiment_name is not None:
        config.mlflow_experiment_name = settings.mlflow_experiment_name

    config.data_dir.mkdir(parents=True, exist_ok=True)
    config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    return config
