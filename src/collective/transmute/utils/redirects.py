from collective.transmute import _types as t
from collective.transmute.settings import get_settings


def initialize_redirects(
    raw_redirects: dict[str, str], settings: t.TransmuteSettings | None = None
) -> dict[str, str]:
    """
    Initialize and normalize a mapping of redirects for migration.

    This function updates source and destination paths in the redirects mapping
    according to the configured site roots in `settings`. If the source and destination
    roots differ, it replaces the source root prefix in both keys and values with the
    destination root, ensuring all redirects are valid for the target site.

    Args:
        raw_redirects (dict[str, str]): Raw mapping of source paths to target paths.
        settings (TransmuteSettings | None): The transmute settings object. If
            `None`, the default settings will be used.

    Returns:
        dict[str, str]: The cleaned and normalized redirects mapping.

    Example:
        >>> redirects = initialize_redirects(settings, raw_redirects)

    Note:
        If the source and destination roots are identical, no replacement occurs.
        Only paths starting with the source root are updated.
    """
    site_root = (settings if settings else get_settings()).site_root
    redirects: dict[str, str] = {}
    src_root: str = site_root["src"]
    dest_root: str = site_root["dest"]
    same_root = src_root == dest_root
    for src, dest in raw_redirects.items():
        if not same_root:
            if src.startswith(src_root):
                src = src.replace(src_root, dest_root, 1)
            if dest.startswith(src_root):
                dest = dest.replace(src_root, dest_root, 1)
        redirects[src] = dest
    return redirects


def add_redirect(
    redirects: dict[str, str], src: str, dest: str, site_root: str
) -> None:
    """
    Add a redirect mapping from source to destination.

    This function adds a new redirect entry to the provided redirects dictionary.
    If the source path already exists in the dictionary, it will be overwritten
    with the new destination path.

    Args:
        redirects (dict[str, str]): The redirects mapping to update.
        src (str): The source path for the redirect.
        dest (str): The destination path for the redirect.

    Example:
        >>> add_redirect(redirects, '/old-path', '/new-path')
    """
    src = src if src.startswith(site_root) else f"{site_root}{src}"
    dest = dest if dest.startswith(site_root) else f"{site_root}{dest}"
    if src == dest:
        # Do nothing if source and destination are the same
        return
    # Add redirect to the list of existing redirects
    redirects[src] = dest


def filter_redirects(
    raw_redirects: dict[str, str], valid_paths: set[str]
) -> dict[str, str]:
    """
    Filter redirects to include only those with valid destination paths.

    This function returns a new dictionary containing only redirects whose
    destination path is either external or present in the set of valid paths.

    Args:
        raw_redirects (dict[str, str]):
            Mapping of source paths to destination paths.
        valid_paths (set[str]):
            Set of valid internal destination paths. Should include site root prefix.

    Returns:
        dict[str, str]:
            Filtered redirects mapping with only valid destinations.

    Example:
        >>> filtered = filter_redirects(raw_redirects, valid_paths)
    """
    redirects = {}
    # Sort paths first
    to_process = sorted(raw_redirects.items())
    for src, dst in to_process:
        is_internal = dst.startswith("/")
        if is_internal and dst not in valid_paths:
            continue
        redirects[src] = dst
    return redirects
