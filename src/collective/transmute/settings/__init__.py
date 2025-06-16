from dynaconf import Dynaconf
from dynaconf import Validator
from pathlib import Path
from typing import Any


def _as_set(value: Any) -> set:
    """Cast value as set."""
    value = value if value else []
    return set(value)


def _settings() -> Dynaconf:
    """Compute settings"""
    local_path = Path(__file__).parent
    default = local_path / "default.toml"
    settings = Dynaconf(
        envvar_prefix="TRANSMUTE",
        preload=[default],
        settings_files=["transmute.toml"],
        merge_enabled=True,
        validators=[
            Validator("paths.filter.allowed", cast=_as_set, default=set()),
            Validator("paths.filter.drop", cast=_as_set, default=set()),
        ],
    )
    if not len(settings.pipeline.get("steps")):
        settings.pipeline.steps = settings.pipeline.default_steps
    return settings


pb_config: Dynaconf = _settings()

is_debug: bool = pb_config.config.debug

__all__ = ["is_debug,pb_config"]
