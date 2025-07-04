from collective.transmute import _types as t
from copy import deepcopy
from dynaconf import Dynaconf
from dynaconf import Validator
from dynaconf.base import Settings
from pathlib import Path


SETTINGS_FILE = "transmute.toml"


def _as_set(value: list) -> set:
    """Cast value as set."""
    value = value if value else []
    return set(value)


def _as_tuple(value: list) -> tuple:
    """Cast value as tuple."""
    value = value if value else []
    return tuple(value)


_SET_SETTINGS = {"cast": _as_set, "default": set()}
_TUPLE_SETTINGS = {"cast": _as_tuple, "default": ()}


_VALIDATORS: dict[str, list[dict]] = {
    "pipeline.steps": [{"len_min": 1}, _TUPLE_SETTINGS],
    "pipeline.do_not_add_drop": [
        _TUPLE_SETTINGS,
    ],
    "principals.remove": [
        _TUPLE_SETTINGS,
    ],
    "default_pages.keys_from_parent": [
        _TUPLE_SETTINGS,
    ],
    "review_state.filter.allowed": [
        _TUPLE_SETTINGS,
    ],
    "paths.filter.allowed": [
        _SET_SETTINGS,
    ],
    "paths.filter.drop": [
        _SET_SETTINGS,
    ],
    "paths.export_prefixes": [
        _TUPLE_SETTINGS,
    ],
    "images.to_preview_image_link": [
        _TUPLE_SETTINGS,
    ],
    "sanitize.drop_keys": [
        _TUPLE_SETTINGS,
    ],
    "sanitize.block_keys": [
        _TUPLE_SETTINGS,
    ],
}


def settings_validators() -> tuple[Validator, ...]:
    """Return validators for the settings."""
    validators = []
    for key, checks in _VALIDATORS.items():
        for kwargs in checks:
            validators.append(Validator(key, **kwargs))
    return tuple(validators)


def _find_config_path(settings: Settings | Dynaconf) -> Path:
    """Return the parent folder of the repository.toml."""
    settings_path = Path(settings.find_file(SETTINGS_FILE))
    return settings_path.resolve()


def parse_default() -> dict:
    """Parse default transmute settings."""
    validators = settings_validators()
    cwd_path = Path(__file__).parent
    settings_file = cwd_path / "default.toml"
    settings = Dynaconf(
        settings_files=[settings_file],
        merge_enabled=False,
        validators=validators,
    )
    return settings.as_dict()


def parse_config(cwd_path: Path) -> dict:
    """Parse transmute config settings."""
    settings = Dynaconf(
        envvar_prefix="TRANSMUTE",
        root_path=cwd_path,
        settings_files=[SETTINGS_FILE],
        merge_enabled=False,
    )
    filepath = _find_config_path(settings)
    if filepath.is_dir():
        raise FileNotFoundError(
            f"Transmute settings file '{SETTINGS_FILE}' not found in {cwd_path}."
        )
    settings.config.filepath = str(filepath)
    return settings.as_dict()


def _merge_dicts(defaults: dict, settings: dict) -> dict:
    """Merge two dictionaries, with settings overriding defaults.

    - If a key exists in both and values are dicts, they are merged recursively.
    - Otherwise, the value from dict2 overwrites the value from dict1.

    Returns a new merged dictionary (does not modify the originals).
    """
    result = defaults.copy()
    for key, value in settings.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def _update_value(data: dict, key: str, cast) -> dict:
    parts = key.split(".")
    value = data
    parent = data
    for part in parts:
        parent = value
        value = value[part]
    parent[part] = cast(value)
    return data


def _merge_defaults(defaults: dict, settings: dict) -> dict:
    """Merge default settings with user settings."""
    merged = {k.lower(): v for k, v in defaults.items()}
    settings = {k.lower(): v for k, v in settings.items()}
    for key, value in settings.items():
        if isinstance(value, dict) and key in merged:
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    # Store the raw data to be used with cli settings command.
    raw_data = deepcopy(merged)
    raw_data["config"].pop("filepath", None)
    merged["_raw_data"] = raw_data
    # Apply validators to the merged settings.
    for key, checks in _VALIDATORS.items():
        for kwargs in checks:
            if cast := kwargs.get("cast"):
                merged = _update_value(merged, key, cast)
    return merged


def get_settings(cwd_path: Path | None = None) -> t.TransmuteSettings:
    """Get the transmute settings."""
    cwd_path = Path.cwd() if cwd_path is None else cwd_path
    defaults = parse_default()
    raw_settings = parse_config(cwd_path)
    payload = _merge_defaults(defaults, raw_settings)
    data = t.TransmuteSettings(**payload)
    return data
