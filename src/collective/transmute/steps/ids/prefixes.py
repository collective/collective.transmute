from collective.transmute import _types as t


def _prefixes_from_settings(
    settings: t.TransmuteSettings,
) -> tuple[tuple[str, str], ...]:
    """Get prefix replacements from settings."""
    steps = settings.steps
    paths = steps.get("paths", {})
    prefixes = paths.get("prefix_replacement", {})
    return tuple(prefixes.items())


def get_prefixes(
    state: t.PipelineState, settings: t.TransmuteSettings
) -> tuple[tuple[str, str], ...]:
    """Get the list of (source, replacement) prefixes from settings."""
    anno = state.annotations
    paths = state.annotations.get("paths", {})
    if not (paths := state.annotations.get("paths", {})):
        anno["paths"] = paths
    if not (prefixes := paths.get("prefix_replacement")):
        prefixes = _prefixes_from_settings(settings)
        anno["paths"]["prefix_replacement"] = prefixes
    return prefixes


def _path_prefixes(prefixes: tuple[tuple[str, str], ...], path: str) -> str:
    """
    Process path prefixes, replacing source prefixes with target prefixes.
    """
    new_path = path
    for prefix, replacement in prefixes:
        if not new_path.startswith(prefix):
            continue
        elif new_path == prefix:
            new_path = new_path.replace(prefix, replacement, 1)
        else:
            # Only replace if it's a full path segment
            new_path = new_path.replace(f"{prefix}/", f"{replacement}/", 1)
    return new_path


def path_prefixes(
    state: t.PipelineState, settings: t.TransmuteSettings, path: str
) -> str:
    """
    Process path prefixes for a given path.
    """
    prefixes = get_prefixes(state, settings)
    return _path_prefixes(prefixes, path)
