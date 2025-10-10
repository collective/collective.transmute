from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import TypedDict


__all__ = ["TransmuteSettings"]


class TransmuteSettingsConfig(TypedDict):
    """Transmute config settings."""

    filepath: Path
    debug: bool
    log_file: str
    report: int
    prepare_data_location: Path
    reports_location: Path


class TransmuteSettingsPipeline(TypedDict):
    steps: tuple[str]
    loader_steps: tuple[str]
    prepare_steps: tuple[str]
    do_not_add_drop: tuple[str, ...]


class TransmuteSettingsSiteRoot(TypedDict):
    src: str
    dest: str


class TransmuteSettingsPrincipals(TypedDict):
    default: str
    remove: tuple[str, ...]


class TransmuteSettingsDefaultPages(TypedDict):
    keep: bool
    keys_from_parent: tuple[str, ...]


class ReviewStateFilter(TypedDict):
    allowed: tuple[str, ...]


class ReviewStateRewrite(TypedDict):
    states: dict[str, str]
    workflows: dict[str, str]


class TransmuteSettingsReviewState(TypedDict):
    filter: ReviewStateFilter
    rewrite: ReviewStateRewrite


class PathsFilter(TypedDict):
    allowed: set[str]
    drop: set[str]


class TransmuteSettingsPaths(TypedDict):
    export_prefixes: tuple[str, ...]
    cleanup: dict[str, str]
    filter: PathsFilter
    portal_type: dict[str, str]


class TransmuteSettingsImages(TypedDict):
    to_preview_image_link: tuple[str, ...]


class TransmuteSettingsSanitize(TypedDict):
    drop_keys: tuple[str, ...]
    block_keys: tuple[str, ...]


@dataclass
class TransmuteSettings:
    """Settings for the Transmute application."""

    config: TransmuteSettingsConfig
    pipeline: TransmuteSettingsPipeline
    site_root: TransmuteSettingsSiteRoot
    principals: TransmuteSettingsPrincipals
    default_pages: TransmuteSettingsDefaultPages
    review_state: TransmuteSettingsReviewState
    paths: TransmuteSettingsPaths
    images: TransmuteSettingsImages
    sanitize: TransmuteSettingsSanitize
    data_override: dict[str, dict[str, Any]]
    types: dict[str, Any]
    steps: dict[str, Any] = field(default_factory=dict)
    _raw_data: dict[str, Any] = field(repr=False, default_factory=dict)

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.get("debug", False)

    @property
    def do_not_add_drop(self) -> tuple[str, ...]:
        """Steps that should not add to the drop list."""
        return self.pipeline["do_not_add_drop"]

    @property
    def paths_filter_allowed(self) -> set[str]:
        """Return list of allowed paths."""
        return self.paths["filter"]["allowed"]
