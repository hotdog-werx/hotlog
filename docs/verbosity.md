# Verbosity Configuration

Hotlog provides a simplified verbosity configuration system that automatically
detects CI environments and supports standard CLI patterns.

## Quick Start

```python
import argparse
from hotlog import add_verbosity_argument, configure_logging, get_logger, resolve_verbosity

# Setup CLI
parser = argparse.ArgumentParser()
add_verbosity_argument(parser)
args = parser.parse_args()

# Configure logging with automatic CI detection
verbosity = resolve_verbosity(args)
configure_logging(verbosity=verbosity)
logger = get_logger(__name__)
```

## Verbosity Levels

- **Level 0** (default): Essential info only, supports live updates
- **Level 1** (`-v`): More verbose, messages stay visible
- **Level 2** (`-vv`): All debug info, no live updates

## API Functions

### `add_verbosity_argument(parser)`

Adds the standard `-v/--verbose` argument to an argparse parser.

```python
import argparse
from hotlog import add_verbosity_argument

parser = argparse.ArgumentParser()
add_verbosity_argument(parser)
args = parser.parse_args()  # Now supports -v and -vv
```

### `get_verbosity_from_env()`

Detects verbosity from environment variables:

1. **`HOTLOG_VERBOSITY`**: Explicit override (0, 1, or 2)
2. **`RUNNER_DEBUG=1`** or **`ACTIONS_RUNNER_DEBUG=true`**: GitHub Actions debug
   mode → level 2
3. **`CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `CIRCLECI`, etc.**: CI environment →
   level 1
4. Default: level 0

```python
from hotlog import get_verbosity_from_env

# Returns 1 when CI=true is set
# Returns 2 when RUNNER_DEBUG=1 is set
verbosity = get_verbosity_from_env()
```

### `resolve_verbosity(args)`

Combines CLI arguments and environment detection. Takes the **maximum** of both
sources, so CLI can override environment or vice versa.

```python
import argparse
from hotlog import add_verbosity_argument, resolve_verbosity

parser = argparse.ArgumentParser()
add_verbosity_argument(parser)
args = parser.parse_args()

# Uses max(CLI verbosity, environment verbosity)
verbosity = resolve_verbosity(args)
```

## Environment Variables

| Variable                    | Effect                                |
| --------------------------- | ------------------------------------- |
| `HOTLOG_VERBOSITY`          | Explicit verbosity level (0, 1, or 2) |
| `RUNNER_DEBUG=1`            | GitHub Actions debug mode (level 2)   |
| `ACTIONS_RUNNER_DEBUG=true` | GitHub Actions debug mode (level 2)   |
| `CI=true`                   | CI environment detected (level 1)     |
| `GITHUB_ACTIONS=true`       | GitHub Actions detected (level 1)     |
| `GITLAB_CI=true`            | GitLab CI detected (level 1)          |
| `CIRCLECI=true`             | CircleCI detected (level 1)           |
| `TRAVIS=true`               | Travis CI detected (level 1)          |
| `JENKINS_HOME`              | Jenkins detected (level 1)            |
| `BUILDKITE=true`            | Buildkite detected (level 1)          |

## Examples

### Basic CLI Usage

```python
from hotlog import add_verbosity_argument, configure_logging, resolve_verbosity, get_logger

parser = argparse.ArgumentParser()
add_verbosity_argument(parser)
args = parser.parse_args()

configure_logging(verbosity=resolve_verbosity(args))
logger = get_logger(__name__)

logger.info("message", _verbose_detail="shown with -v", _debug_info="shown with -vv")
```

### CI Auto-Detection

When running in CI, verbosity is automatically set to 1:

```bash
# Locally: verbosity 0
python my_script.py

# In GitHub Actions: verbosity 1 (auto-detected)
# In GitHub Actions with debug: verbosity 2 (auto-detected)

# Override: verbosity 2
python my_script.py -vv
```

### Manual Environment Override

```bash
# Force verbosity to 2
HOTLOG_VERBOSITY=2 python my_script.py

# CLI takes precedence (uses max of both)
CI=true python my_script.py -vv  # Uses level 2
```

## Migration from Manual Setup

### Before

```python
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()
verbosity = min(args.verbose, 2)
configure_logging(verbosity=verbosity)
```

### After

```python
add_verbosity_argument(parser)
args = parser.parse_args()
configure_logging(verbosity=resolve_verbosity(args))  # Now with CI detection!
```
