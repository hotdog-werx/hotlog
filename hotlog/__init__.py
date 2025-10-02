"""
hotlog: Generalized logging utility for Python projects

Provides three levels of verbosity:
- Level 0 (default): Essential info with live updates that can disappear
- Level 1 (-v): More verbose, messages stay visible
- Level 2 (-vv): All debug messages, no live updates

Usage:
    from hotlog import get_logger, configure_logging, ToolMatch

    configure_logging(
        verbosity=0,
        matchers=[
            ToolMatch(event="executing", prefix="tb")
        ]
    )
    logger = get_logger(__name__)
"""

import logging
import structlog
import yaml
import sys
from rich.console import Console
from rich.syntax import Syntax
from rich.live import Live
from contextlib import contextmanager
from structlog.types import FilteringBoundLogger
from structlog.typing import EventDict
from typing import Callable, Optional, List
from dataclasses import dataclass


def _get_console() -> Console:
    """Get a Console instance that writes to the current sys.stdout.
    
    This ensures compatibility with pytest's output capturing by always
    using the current sys.stdout, not a cached version. We don't force
    terminal mode but ensure output is not suppressed.
    """
    return Console(file=sys.stdout, force_jupyter=False)

# Type alias for our logger
Logger = FilteringBoundLogger

# Default prefixes for context filtering
DEFAULT_PREFIXES = ["_verbose_", "_debug_", "_perf_", "_security_"]

# Global verbosity level (0=default, 1=verbose, 2=debug)
_VERBOSITY_LEVEL = 0

# Global matchers for custom formatting
_MATCHERS = []

# Global live context (for level 0 only)
_LIVE_CONTEXT = None
_LIVE_MESSAGES = []  # Buffer messages during live context


@dataclass
class LogMatcher:
    """Base class for log message matchers."""

    def matches(self, level: str, event: str, event_dict: EventDict) -> bool:
        """Check if this matcher applies to the log message.

        Args:
            level: Log level (INFO, WARNING, etc.)
            event: Event message
            event_dict: Event context dictionary

        Returns:
            True if this matcher should handle the message
        """
        raise NotImplementedError

    def format(
        self,
        level: str,
        event: str,
        event_dict: EventDict,
    ) -> Optional[str]:
        """Format the log message.

        Args:
            level: Log level
            event: Event message
            event_dict: Event context dictionary (will be modified)

        Returns:
            Formatted message string, or None to use default formatting
        """
        raise NotImplementedError


@dataclass
class ToolMatch(LogMatcher):
    """Matcher for tool execution logs (toolbelt style).

    Matches logs with specific event name and required keys,
    then formats them as: prefix[tool] => command

    Args:
        event: Event name to match (default: "executing")
        prefix: Prefix to show (default: "tb")
        level: Log level to match (default: "INFO")
        command_key: Key containing the command (default: "command")
        tool_key: Key containing the tool name (default: "tool")
    """

    event: str = "executing"
    prefix: str = "tb"
    level: str = "INFO"
    command_key: str = "command"
    tool_key: str = "tool"

    def matches(self, level: str, event: str, event_dict: EventDict) -> bool:
        return (
            level == self.level
            and event == self.event
            and self.command_key in event_dict
        )

    def format(
        self,
        level: str,
        event: str,
        event_dict: EventDict,
    ) -> Optional[str]:
        command = event_dict.pop(self.command_key)
        tool_name = event_dict.pop(self.tool_key, "")

        if tool_name:
            return f"[bold #888888]{self.prefix}\\[{tool_name}] =>[/bold #888888] [blue]{command}[/blue]"
        else:
            return f"[blue]{command}[/blue]"


def format_context_yaml(event_dict: EventDict, indent: int = 2) -> str:
    """Format the context dictionary as YAML.

    Args:
        event_dict: The context dictionary to format.
        indent: The number of spaces to use for indentation.

    Returns:
        The formatted YAML string.
    """
    if not event_dict:
        return ""
    context_yaml = yaml.safe_dump(
        event_dict,
        sort_keys=True,
        default_flow_style=False,
    )
    pad = " " * indent
    return "\n".join(f"{pad}{line}" for line in context_yaml.splitlines())


def pre_process_log(event_msg: str, event_dict: EventDict) -> str:
    """Custom log formatting for command execution events.

    Args:
        event_msg: The main event message.
        event_dict: The event dictionary containing additional context.

    Returns:
        The processed event message.
    """
    # Remove internal structlog keys
    for key in ("timestamp", "level", "log_level", "event"):
        event_dict.pop(key, None)
    return event_msg


def filter_context_by_prefix(event_dict: EventDict) -> EventDict:
    """Filter context dictionary based on key prefixes and verbosity level.

    - Level 0: Only keys without _verbose_ or _debug_ prefixes
    - Level 1: Keys without _debug_ prefix (includes _verbose_)
    - Level 2: All keys

    Prefixes are stripped from the keys when displayed.
    """
    global _VERBOSITY_LEVEL

    if _VERBOSITY_LEVEL >= 2:
        # Debug mode: show everything
        return event_dict

    filtered_dict = {}
    for key, value in event_dict.items():
        if _VERBOSITY_LEVEL == 0:
            # Default mode: filter out _verbose_ and _debug_
            if key.startswith("_verbose_") or key.startswith("_debug_"):
                continue
        elif _VERBOSITY_LEVEL == 1:
            # Verbose mode: only filter out _debug_
            if key.startswith("_debug_"):
                continue

        filtered_dict[key] = value

    return filtered_dict


def strip_prefixes_from_keys(event_dict: EventDict) -> EventDict:
    """Strip display prefixes from keys for cleaner output."""
    display_prefixes = ["_verbose_", "_debug_", "_perf_", "_security_"]

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


def cli_renderer(
    _logger: Logger,
    method_name: str,
    event_dict: EventDict,
) -> str:
    """Render log messages for CLI output using rich formatting.

    Args:
        _logger: The logger instance.
        method_name: The logging method name (e.g., 'info', 'error').
        event_dict: The event dictionary containing log data.

    Returns:
        str: An empty string, as structlog expects a string return but output is printed.
    """
    global _LIVE_CONTEXT, _LIVE_MESSAGES, _VERBOSITY_LEVEL, _MATCHERS

    level = method_name.upper()
    event_msg = event_dict.pop("event", "")

    # Check if this is a live message (should be buffered at level 0)
    is_live_message = event_dict.pop("_live_", False)

    # Pre-process to remove internal keys
    event_msg = pre_process_log(event_msg, event_dict)

    # Try matchers first for custom formatting
    log_msg = None
    for matcher in _MATCHERS:
        if matcher.matches(level, event_msg, event_dict):
            log_msg = matcher.format(level, event_msg, event_dict)
            if log_msg is not None:
                break

    # If no matcher handled it, use default formatting
    if log_msg is None:
        # Filter context based on verbosity level
        event_dict = filter_context_by_prefix(event_dict)

        # Always strip prefixes for clean display
        event_dict = strip_prefixes_from_keys(event_dict)

        context_yaml = format_context_yaml(event_dict)

        # Map log levels to colors/styles
        level_styles = {
            "INFO": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "DEBUG": "magenta",
            "CRITICAL": "white on red",
            "SUCCESS": "green",
        }

        # Pick style, fallback to bold cyan for unknown
        style = level_styles.get(level, "bold cyan")

        # Clean output without level prefix (uv style)
        if level == "DEBUG":
            # Show DEBUG prefix only in debug mode
            log_msg = f"[{style}]DEBUG[/{style}] [{style}]{event_msg}[/{style}]"
        elif level in ("WARNING", "ERROR", "CRITICAL"):
            # Show level for warnings and errors (important)
            log_msg = f"[bold {style}]{level}:[/bold {style}] [{style}]{event_msg}[/{style}]"
        else:
            # INFO and SUCCESS: no prefix, just the message
            log_msg = f"[{style}]{event_msg}[/{style}]"
    else:
        # Matcher provided formatting, still need to process context
        event_dict = filter_context_by_prefix(event_dict)
        event_dict = strip_prefixes_from_keys(event_dict)
        context_yaml = format_context_yaml(event_dict)

    # Check if we should buffer this message (live context at level 0)
    if is_live_message and _LIVE_CONTEXT is not None and _VERBOSITY_LEVEL == 0:
        # At level 0 with live context: buffer messages, don't print them yet
        # They will be cleared when the live context exits
        _LIVE_MESSAGES.append((log_msg, context_yaml))
        # Update live display to show we're processing
        if _LIVE_MESSAGES:
            # Show the messages in the live area temporarily
            display_lines = []
            for msg, ctx in _LIVE_MESSAGES:
                display_lines.append(msg)
                if ctx:
                    # Indent context for better readability
                    for line in ctx.split("\n"):
                        display_lines.append(f"  {line}")
            _LIVE_CONTEXT.update("\n".join(display_lines))
    else:
        # Normal mode or level 1+: print to console directly
        console = _get_console()
        console.print(log_msg)
        if context_yaml:
            syntax = Syntax(
                context_yaml,
                "yaml",
                theme="github-dark",
                background_color="default",
                line_numbers=False,
            )
            console.print(syntax)

    return ""  # structlog expects a string return, but we already printed


def configure_logging(
    verbosity: int = 0,
    renderer: Optional[Callable] = None,
    matchers: Optional[List[LogMatcher]] = None,
) -> None:
    """Configure structlog for hotlog.

    Args:
        verbosity: Verbosity level (0=default, 1=verbose, 2=debug)
                  - 0: Essential info only, supports live updates
                  - 1: More context, messages stay visible
                  - 2: All debug info, no live updates
        renderer: Custom renderer function (optional)
        matchers: List of LogMatcher instances for custom log formatting.
                 Example: [ToolMatch(event="executing", prefix="tb")]
    """
    global _VERBOSITY_LEVEL, _MATCHERS
    _VERBOSITY_LEVEL = verbosity
    _MATCHERS = matchers or []

    chosen_renderer = renderer or cli_renderer

    # Reset structlog to clear any cached loggers
    structlog.reset_defaults()
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="ISO", utc=False),
            structlog.stdlib.add_log_level,
            chosen_renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Set log level based on verbosity
    # Clear existing handlers and set up a basic console handler
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Clear existing handlers
    root_logger.setLevel(logging.DEBUG if verbosity >= 2 else logging.INFO)


class LiveLogger:
    """Logger wrapper that buffers messages during live context at level 0."""

    def __init__(self, base_logger: Logger, is_live_mode: bool):
        self._logger = base_logger
        self._is_live_mode = is_live_mode

    def info(self, event: str, **kwargs):
        """Log info message (buffered in live mode at level 0)."""
        if self._is_live_mode:
            # Mark this as a live message so the renderer knows to buffer it
            kwargs["_live_"] = True
        self._logger.info(event, **kwargs)

    def debug(self, event: str, **kwargs):
        """Log debug message (buffered in live mode at level 0)."""
        if self._is_live_mode:
            kwargs["_live_"] = True
        self._logger.debug(event, **kwargs)

    def warning(self, event: str, **kwargs):
        """Log warning message (buffered in live mode at level 0)."""
        if self._is_live_mode:
            kwargs["_live_"] = True
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs):
        """Log error message (always visible, never buffered)."""
        # Errors should always be visible
        self._logger.error(event, **kwargs)


def get_logger(name: str) -> Logger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def highlight(text: str, *values) -> str:
    """Helper to highlight specific values in a message.

    Useful for emphasizing important information in log messages.

    Args:
        text: Format string with {} placeholders
        *values: Values to highlight (will be bolded)

    Returns:
        String with Rich markup for bold values

    Example:
        logger.info(highlight("Installed {} in {}", "5 packages", "3ms"))
        # Renders as: "Installed [bold]5 packages[/bold] in [bold]3ms[/bold]"
    """
    bold_values = [f"[bold]{v}[/bold]" for v in values]
    return text.format(*bold_values)


@contextmanager
def live_logging(message: str = "Processing..."):
    """Context manager for live logging with dynamic behavior based on verbosity.

    Returns a LiveLogger that:
    - At level 0: Buffers messages in live area (disappear when done)
    - At level 1+: Logs normally (messages stay visible)

    Usage:
        with live_logging("Downloading files...") as live:
            live.info("Downloaded file 1")  # disappears at level 0, stays at level 1+
            live.info("Downloaded file 2")  # disappears at level 0, stays at level 1+

        logger.info("Download completed")  # always visible (summary)

    Args:
        message: The live status message to display
    """
    global _LIVE_CONTEXT, _LIVE_MESSAGES, _VERBOSITY_LEVEL

    base_logger = get_logger("live")

    if _VERBOSITY_LEVEL == 0:
        # Level 0: Use live display with buffering
        _LIVE_MESSAGES = []  # Clear message buffer
        with Live(
            f"[bold blue]{message}[/bold blue]",
            console=_get_console(),
            refresh_per_second=10,
            transient=True,  # Makes the live display disappear when done!
        ) as live:
            _LIVE_CONTEXT = live
            try:
                # Return a LiveLogger that marks messages for buffering
                yield LiveLogger(base_logger, is_live_mode=True)
            finally:
                _LIVE_CONTEXT = None
                _LIVE_MESSAGES = []  # Clear buffered messages (they disappear)
    else:
        # Level 1+: Just print header and return LiveLogger without buffering
        _get_console().print(f"[bold blue]{message}[/bold blue]")
        # Return LiveLogger that doesn't mark messages for buffering
        yield LiveLogger(base_logger, is_live_mode=False)


# Public API
__all__ = [
    "configure_logging",
    "get_logger",
    "live_logging",
    "highlight",
    "LogMatcher",
    "ToolMatch",
]
