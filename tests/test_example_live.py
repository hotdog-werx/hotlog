"""Parametrized tests for example_live.py"""

import pytest

from tests.test_helpers import level_0, level_1, level_2, verify_output

LIVE_EXPECTATIONS = [
    level_0(
        'Download completed',
        'total_files: 42',
        'Extraction completed',
        'Installation completed with errors',
        'Package installation failed',
        'Example completed',
        'verbosity level 0',
        should_not_contain=[
            '_verbose_duration',
            '_verbose_compression',
            'Connected to server',
            'algorithm:',
        ],
        desc='live messages disappear, errors shown at level 0',
    ),
    level_1(
        'Connected to server',
        'host: github.com',
        'Fetching metadata',
        'size: 2.5MB',
        'Unpacking archive',
        'compression: gzip',
        'Installed package 1/5',
        'Installed package 5/5',
        'duration: 3.2s',
        'package: package-1',
        'package: package-5',
        'Large file detected',
        'file_size: 250MB',
        should_not_contain=[
            '_debug_algorithm',
            'algorithm:',
            'Validating checksums',
        ],
        desc='live messages visible, verbose context shown, debug hidden at level 1',
    ),
    level_2(
        'Connected to server',
        'Fetching metadata',
        'Unpacking archive',
        'Validating checksums',
        'Large file detected',
        'file_size: 250MB',
        'Package installation failed',
        'Installed package 1/5',
        'Installed package 2/5',
        'Installed package 4/5',
        'Installed package 5/5',
        'duration: 3.2s',
        'compression: gzip',
        'algorithm: sha256',
        desc='all messages including debug visible at level 2',
    ),
    level_0(
        'Download completed',
        'Extraction completed',
        'Installation completed with errors',
        'Package installation failed',
        desc='live_logging context manager works, error messages shown',
    ),
]


@pytest.mark.parametrize(
    'expectation',
    LIVE_EXPECTATIONS,
    ids=lambda e: e.description,
)
def test_live_output(run_example_live, expectation):
    """Test example_live output at different verbosity levels."""
    result = run_example_live(expectation.args)
    verify_output(result, expectation)
