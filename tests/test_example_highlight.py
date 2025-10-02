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
        # Level 0 - Basic output without verbose context
        level_0(
            'Installed 5 packages in 3ms',
            'Downloaded 14 files in 2.5s',
            'Processing 100 records from database',
            'Resolved 42 dependencies with no conflicts in 150ms',
            'Cache size: 2.5GB (1,234 entries)',
            'Rate limit approaching: 95 requests of 100 requests used',
            'Examples completed',
            'verbosity level: 0',
            should_not_contain=[
                '_verbose_packages',
                '_verbose_registry',
            ],
            desc='basic_messages_without_verbose_context',
        ),
        # Level 1 - Verbose context visible
        level_1(
            'Resolved 42 dependencies with no conflicts in 150ms',
            'packages:',
            'react, vue, angular',
            'registry:',
            'https://registry.npmjs.org',
            'Compilation completed: 95 files successful, 5 files failed',
            'duration:',
            '5.2s',
            'warnings:',
            '12',
            'verbosity level: 1',
            should_not_contain=[
                '_verbose_packages',
                '_verbose_registry',
            ],
            desc='verbose_context_visible',
        ),
        # Test highlight() helper specifically
        level_0(
            'Downloaded 14 files in 2.5s',
            desc='highlight()_helper_works',
        ),
        # Test warning messages
        level_0(
            'Rate limit approaching: 95 requests of 100 requests used',
            desc='warnings_shown_at_level_0',
        ),
    ],
    ids=lambda e: e.description,
)
def test_highlight_output(
    run_example_highlight: ExampleRunner,
    expectation: OutputExpectation,
):
    """Test example_highlight output at different verbosity levels."""
    result = run_example_highlight(expectation.args)
    verify_output(result, expectation)
