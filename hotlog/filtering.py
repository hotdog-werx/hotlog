"""Context filtering based on verbosity level and key prefixes."""

from structlog.typing import EventDict

from hotlog.config import DEFAULT_PREFIXES, get_verbosity_level


def filter_context_by_prefix(event_dict: EventDict) -> EventDict:
    """Filter context dictionary based on key prefixes and verbosity level.

    - Level 0: Only keys without _verbose_ or _debug_ prefixes
    - Level 1: Keys without _debug_ prefix (includes _verbose_)
    - Level 2: All keys

    Prefixes are NOT stripped by this function - that's done by strip_prefixes_from_keys().

    Args:
        event_dict: Dictionary of context key-value pairs

    Returns:
        Filtered dictionary based on current verbosity level
    """
    verbosity_level = get_verbosity_level()

    if verbosity_level >= 2:
        # Debug mode: show everything
        return event_dict

    filtered_dict = {}
    for key, value in event_dict.items():
        if verbosity_level == 0:
            # Default mode: filter out _verbose_ and _debug_
            if key.startswith('_verbose_') or key.startswith('_debug_'):
                continue
        elif verbosity_level == 1:
            # Verbose mode: only filter out _debug_
            if key.startswith('_debug_'):
                continue

        filtered_dict[key] = value

    return filtered_dict


def strip_prefixes_from_keys(event_dict: EventDict) -> EventDict:
    """Strip display prefixes from keys for cleaner output.

    Removes prefixes like _verbose_, _debug_, _perf_, _security_ from keys
    so they display cleanly in the output.

    Args:
        event_dict: Dictionary with potentially prefixed keys

    Returns:
        Dictionary with clean keys (prefixes removed)

    Example:
        >>> strip_prefixes_from_keys({"_verbose_source": "file.py", "count": 42})
        {"source": "file.py", "count": 42}
    """
    display_prefixes = DEFAULT_PREFIXES

    cleaned_dict = {}
    for key, value in event_dict.items():
        clean_key = key
        # Remove any matching prefix
        for prefix in display_prefixes:
            if key.startswith(prefix):
                clean_key = key.removeprefix(prefix)
                break

        cleaned_dict[clean_key] = value

    return cleaned_dict
