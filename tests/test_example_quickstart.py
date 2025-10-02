"""Parametrized tests for example_quickstart.py"""

import pytest

from tests.conftest import ExampleRunner
from tests.test_helpers import (
    OutputExpectation,
    level_0,
    level_1,
    level_2,
    verify_output,
)


@pytest.mark.parametrize(
    'expectation',
    [
        level_0(
            'Quick Start Example',
            'Application starting',
            'version: 1.0.0',
            'Loaded 50 plugins in 120ms',
            'Configuration loaded',
            'env: production',
            'myapp[docker-build]',
            'docker build -t myapp:latest .',
            'API rate limit at 80%',
            'current: 80',
            'limit: 100',
            'Downloaded 3 packages successfully',
            'Tips:',
            'verbosity level: 0',
            should_not_contain=[
                'config_file:',
                'raw_config:',
                '_verbose_layers',
                'layers:',
                'build_context:',
                'size: 2MB',
            ],
            desc='basic_messages,_warnings_shown,_verbose/debug_hidden_at_level_0',
        ),
        level_1(
            'Configuration loaded',
            'config_file: /etc/myapp/config.yaml',
            'myapp[docker-build]',
            'layers: 12',
            'Downloaded package-1',
            'Downloaded package-2',
            'Downloaded package-3',
            'size: 2MB',
            'size: 4MB',
            'size: 6MB',
            'verbosity level: 1',
            should_not_contain=['raw_config:', 'build_context:'],
            desc='verbose_context_and_live_logging_visible,_debug_hidden_at_level_1',
        ),
        level_2(
            'Configuration loaded',
            'config_file: /etc/myapp/config.yaml',
            'raw_config:',
            'myapp[docker-build]',
            'layers: 12',
            'build_context: /tmp/build-123',
            'verbosity level: 2',
            desc='all_context_including_debug_visible_at_level_2',
        ),
    ],
    ids=lambda e: e.description,
)
def test_quickstart_output(
    run_example_quickstart: ExampleRunner,
    expectation: OutputExpectation,
):
    """Test example_quickstart output at different verbosity levels."""
    result = run_example_quickstart(expectation.args)
    verify_output(result, expectation)
