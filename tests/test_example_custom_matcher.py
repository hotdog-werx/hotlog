"""Parametrized tests for example_custom_matcher.py"""

import pytest

from tests.conftest import ExampleRunner
from tests.test_helpers import (
    OutputExpectation,
    level_0,
    level_1,
    verify_output,
)


@pytest.mark.parametrize(
    'expectation',
    [
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
            desc='all_custom_matchers_work_at_default_verbosity',
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
            desc='verbose_context_visible_with_all_matchers',
        ),
        level_0(
            'Installed requests (version 2.31.0)',
            'Installed structlog (version 25.4.0)',
            should_not_contain=['localhost:5432'],
            desc='InstallMatch_handles_versions_correctly',
        ),
        level_0(
            '[E001]',
            'Failed to connect to database',
            should_not_contain=['localhost:5432'],
            desc='ErrorMatch_formats_error_codes',
        ),
        level_0(
            'pkg[uv-install] =>',
            'uv pip install requests',
            desc='ToolMatch_formats_tool_execution',
        ),
        level_0(
            'Build completed successfully',
            desc='default_formatting_fallback_works',
        ),
        level_0(
            'Installed requests',
            '[E001]',
            'pkg[uv-install] =>',
            'Build completed successfully',
            desc='multiple_matchers_coexist',
        ),
    ],
    ids=lambda e: e.description,
)
def test_custom_matcher_output(
    run_example_custom_matcher: ExampleRunner,
    expectation: OutputExpectation,
):
    """Test example_custom_matcher output at different verbosity levels."""
    result = run_example_custom_matcher(expectation.args)
    verify_output(result, expectation)
