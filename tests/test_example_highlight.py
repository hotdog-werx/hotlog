"""Parametrized tests for example_highlight.py"""

import pytest

from tests.test_helpers import (
    OutputExpectation,
    level_0,
    level_1,
    verify_output,
)

# Test data for example_highlight using helper functions
HIGHLIGHT_EXPECTATIONS = [
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
        desc='basic messages without verbose context',
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
        desc='verbose context visible',
    ),
    # Test highlight() helper specifically
    level_0(
        'Downloaded 14 files in 2.5s',
        desc='highlight() helper works',
    ),
    # Test warning messages
    level_0(
        'Rate limit approaching: 95 requests of 100 requests used',
        desc='warnings shown at level 0',
    ),
]


@pytest.mark.parametrize(
    'expectation',
    HIGHLIGHT_EXPECTATIONS,
    ids=lambda e: e.description,
)
def test_highlight_output(
    run_example_highlight,
    expectation: OutputExpectation,
):
    """Test example_highlight output at different verbosity levels."""
    result = run_example_highlight(expectation.args)
    verify_output(result, expectation)
