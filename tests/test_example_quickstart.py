"""Parametrized tests for example_quickstart.py"""

import pytest

from tests.test_helpers import level_0, level_1, level_2, verify_output

QUICKSTART_EXPECTATIONS = [
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
        desc='basic messages, warnings shown, verbose/debug hidden at level 0',
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
        desc='verbose context and live logging visible, debug hidden at level 1',
    ),
    level_2(
        'Configuration loaded',
        'config_file: /etc/myapp/config.yaml',
        'raw_config:',
        'myapp[docker-build]',
        'layers: 12',
        'build_context: /tmp/build-123',
        'verbosity level: 2',
        desc='all context including debug visible at level 2',
    ),
]


@pytest.mark.parametrize(
    'expectation',
    QUICKSTART_EXPECTATIONS,
    ids=lambda e: e.description,
)
def test_quickstart_output(run_example_quickstart, expectation):
    """Test example_quickstart output at different verbosity levels."""
    result = run_example_quickstart(expectation.args)
    verify_output(result, expectation)
