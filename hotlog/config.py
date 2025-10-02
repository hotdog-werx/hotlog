"""Global configuration and state management for hotlog."""

import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.live import Live

if TYPE_CHECKING:
    from hotlog.matchers import LogMatcher


# Global verbosity level (0=default, 1=verbose, 2=debug)
_VERBOSITY_LEVEL = 0

# Global matchers for custom formatting
_MATCHERS: list['LogMatcher'] = []

# Global live context (for level 0 only)
_LIVE_CONTEXT: Live | None = None
_LIVE_MESSAGES: list[tuple[str, str]] = []  # Buffer messages during live context

# Default prefixes for context filtering
DEFAULT_PREFIXES = ['_verbose_', '_debug_', '_perf_', '_security_']


def get_console() -> Console:
    """Get a Console instance that writes to the current sys.stdout.

    This ensures compatibility with pytest's output capturing by always
    using the current sys.stdout, not a cached version. We don't force
    terminal mode but ensure output is not suppressed.
    """
    return Console(file=sys.stdout, force_jupyter=False)


def get_verbosity_level() -> int:
    """Get the current verbosity level.

    Returns:
        Current verbosity level (0, 1, or 2)
    """
    return _VERBOSITY_LEVEL


def set_verbosity_level(level: int) -> None:
    """Set the verbosity level.

    Args:
        level: Verbosity level (0=default, 1=verbose, 2=debug)
    """
    global _VERBOSITY_LEVEL
    _VERBOSITY_LEVEL = level


def get_matchers() -> list['LogMatcher']:
    """Get the current list of matchers.

    Returns:
        List of registered LogMatcher instances
    """
    return _MATCHERS


def set_matchers(matchers: list['LogMatcher']) -> None:
    """Set the list of matchers.

    Args:
        matchers: List of LogMatcher instances
    """
    global _MATCHERS
    _MATCHERS = matchers


def get_live_context() -> Live | None:
    """Get the current live context.

    Returns:
        Active Live context or None
    """
    return _LIVE_CONTEXT


def set_live_context(context: Live | None) -> None:
    """Set the live context.

    Args:
        context: Live context instance or None
    """
    global _LIVE_CONTEXT
    _LIVE_CONTEXT = context


def get_live_messages() -> list[tuple[str, str]]:
    """Get the current live message buffer.

    Returns:
        List of (message, context_yaml) tuples
    """
    return _LIVE_MESSAGES


def clear_live_messages() -> None:
    """Clear the live message buffer."""
    global _LIVE_MESSAGES
    _LIVE_MESSAGES = []


def append_live_message(message: str, context_yaml: str) -> None:
    """Append a message to the live buffer.

    Args:
        message: Formatted log message
        context_yaml: Formatted context YAML
    """
    _LIVE_MESSAGES.append((message, context_yaml))
