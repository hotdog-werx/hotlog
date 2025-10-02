"""Parametrized tests for example_custom_matcher.py"""

import pytest

from tests.test_helpers import level_0, level_1, verify_output

CUSTOM_MATCHER_EXPECTATIONS = [
    level_0(
        'Custom Matcher Example (verbosity level: 0)',
        'Installed requests (version 2.31.0)',
        'Installed structlog (version 25.4.0)',
        '[E001]',
        'Failed to connect to database',
        'pkg[uv-install] =>',
        'uv pip install requests',
        'Build completed successfully',
        'Custom matcher example completed',
        should_not_contain=[
            'size: 120 KB',
            'cache_hit: true',
            'host: localhost:5432',
        ],
        desc='all custom matchers work at default verbosity',
    ),
    level_1(
        'Custom Matcher Example (verbosity level: 1)',
        'Installed requests',
        'Installed structlog',
        '[E001]',
        'Failed to connect to database',
        'pkg[uv-install] =>',
        'uv pip install requests',
        'Build completed successfully',
        'size: 120 KB',
        'cache_hit: true',
        'host: localhost:5432',
        desc='verbose context visible with all matchers',
    ),
    level_0(
        'Installed requests (version 2.31.0)',
        'Installed structlog (version 25.4.0)',
        should_not_contain=['localhost:5432'],
        desc='InstallMatch handles versions correctly',
    ),
    level_0(
        '[E001]',
        'Failed to connect to database',
        should_not_contain=['localhost:5432'],
        desc='ErrorMatch formats error codes',
    ),
    level_0(
        'pkg[uv-install] =>',
        'uv pip install requests',
        desc='ToolMatch formats tool execution',
    ),
    level_0(
        'Build completed successfully',
        desc='default formatting fallback works',
    ),
    level_0(
        'Installed requests',
        '[E001]',
        'pkg[uv-install] =>',
        'Build completed successfully',
        desc='multiple matchers coexist',
    ),
]


@pytest.mark.parametrize(
    'expectation',
    CUSTOM_MATCHER_EXPECTATIONS,
    ids=lambda e: e.description,
)
def test_custom_matcher_output(run_example_custom_matcher, expectation):
    """Test example_custom_matcher output at different verbosity levels."""
    result = run_example_custom_matcher(expectation.args)
    verify_output(result, expectation)
