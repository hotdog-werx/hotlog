"""Tests for example_live.py"""


# ============================================================
# Level 0 Tests (Default)
# ============================================================


def test_live_logging_disappears_at_level_0(run_example_live):
    """Test that live messages disappear at verbosity level 0"""
    result = run_example_live([])
    
    # Final messages should appear
    assert "Download completed" in result.stdout
    assert "total_files: 42" in result.stdout
    assert "Extraction completed" in result.stdout
    assert "Installation completed with errors" in result.stdout
    
    # Errors should always show even at level 0
    assert "Package installation failed" in result.stdout
    
    # Verbose context should not appear at level 0
    assert "_verbose_duration" not in result.stdout
    assert "_verbose_compression" not in result.stdout


def test_example_completes_at_level_0(run_example_live):
    """Test that example runs successfully at level 0"""
    result = run_example_live([])
    
    assert result.returncode == 0
    assert "verbosity level 0" in result.stdout
    assert "Example completed" in result.stdout


# ============================================================
# Level 1 Tests (-v)
# ============================================================


def test_live_messages_visible_at_level_1(run_example_live):
    """Test that live messages stay visible at verbosity level 1"""
    result = run_example_live(["-v"])
    
    # Example 1: Download operation messages
    assert "Connected to server" in result.stdout
    assert "host: github.com" in result.stdout
    assert "Fetching metadata" in result.stdout
    assert "size: 2.5MB" in result.stdout
    
    # Example 2: Extract operation messages
    assert "Unpacking archive" in result.stdout
    assert "compression: gzip" in result.stdout
    
    # Example 3: Installation progress
    assert "Installed package 1/5" in result.stdout
    assert "Installed package 5/5" in result.stdout


def test_verbose_context_visible_at_level_1(run_example_live):
    """Test that _verbose_ prefixed context is visible at level 1"""
    result = run_example_live(["-v"])
    
    # Verbose context should appear
    assert "duration: 3.2s" in result.stdout
    assert "compression: gzip" in result.stdout
    assert "size: 2.5MB" in result.stdout
    assert "package: package-1" in result.stdout
    assert "package: package-5" in result.stdout


def test_debug_context_hidden_at_level_1(run_example_live):
    """Test that _debug_ prefixed context is hidden at level 1"""
    result = run_example_live(["-v"])
    
    # Debug context should NOT appear at level 1
    assert "_debug_algorithm" not in result.stdout
    assert "algorithm:" not in result.stdout
    
    # Debug level messages should NOT appear at level 1
    assert "Validating checksums" not in result.stdout


def test_warning_messages_visible_at_level_1(run_example_live):
    """Test that live.warning() messages are visible at level 1"""
    result = run_example_live(["-v"])
    
    # Warning messages should appear at level 1
    assert "Large file detected" in result.stdout
    assert "file_size: 250MB" in result.stdout


# ============================================================
# Level 2 Tests (-vv)
# ============================================================


def test_debug_context_visible_at_level_2(run_example_live):
    """Test that _debug_ prefixed context is visible at level 2"""
    result = run_example_live(["-v", "-v"])
    
    # All context including debug should appear
    assert "duration: 3.2s" in result.stdout
    assert "compression: gzip" in result.stdout
    assert "algorithm: sha256" in result.stdout
    
    # Debug level messages should appear at level 2
    assert "Validating checksums" in result.stdout


def test_warning_messages_visible_at_level_2(run_example_live):
    """Test that live.warning() messages are visible at level 2"""
    result = run_example_live(["-v", "-v"])
    
    # Warning messages should appear
    assert "Large file detected" in result.stdout
    assert "file_size: 250MB" in result.stdout


def test_all_messages_visible_at_level_2(run_example_live):
    """Test that all live messages are visible at level 2"""
    result = run_example_live(["-v", "-v"])
    
    # All messages from all examples should be visible
    assert "Connected to server" in result.stdout
    assert "Fetching metadata" in result.stdout
    assert "Unpacking archive" in result.stdout
    assert "Validating checksums" in result.stdout  # debug level message
    assert "Large file detected" in result.stdout  # warning level message
    assert "Package installation failed" in result.stdout  # error level message
    assert "Installed package 1/5" in result.stdout
    assert "Installed package 2/5" in result.stdout
    # Package 3 fails
    assert "Installed package 4/5" in result.stdout
    assert "Installed package 5/5" in result.stdout


def test_error_messages_always_shown(run_example_live):
    """Test that live.error() messages are always shown"""
    result_0 = run_example_live([])
    result_1 = run_example_live(["-v"])
    result_2 = run_example_live(["-v", "-v"])
    
    # Error messages should appear at all levels
    assert "Package installation failed" in result_0.stdout
    assert "Package installation failed" in result_1.stdout
    assert "Package installation failed" in result_2.stdout


# ============================================================
# General Behavior Tests
# ============================================================


def test_live_logging_context_manager(run_example_live):
    """Test that live_logging context manager works correctly"""
    result = run_example_live([])
    
    # Should complete without error (even though there's an error message in the example)
    assert result.returncode == 0
    
    # Final summary messages should appear
    assert "Download completed" in result.stdout
    assert "Extraction completed" in result.stdout
    assert "Installation completed with errors" in result.stdout
    
    # Error messages should appear
    assert "Package installation failed" in result.stdout


def test_verbosity_levels_accepted(run_example_live):
    """Test that different verbosity levels are accepted"""
    result_0 = run_example_live([])
    result_1 = run_example_live(["-v"])
    result_2 = run_example_live(["-v", "-v"])
    
    assert result_0.returncode == 0
    assert result_1.returncode == 0
    assert result_2.returncode == 0
    
    assert "verbosity level 0" in result_0.stdout
    assert "verbosity level 1" in result_1.stdout
    assert "verbosity level 2" in result_2.stdout
