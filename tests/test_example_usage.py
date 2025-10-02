"""Tests for example_usage.py"""


# ============================================================
# Level 0 Tests (Default)
# ============================================================


def test_basic_usage_level_0(run_example_usage):
    """Test basic messages at verbosity level 0"""
    result = run_example_usage([])
    
    # Basic messages should appear
    assert "Starting example application" in result.stdout
    assert "app_version: 1.0.0" in result.stdout
    assert "Processing data" in result.stdout
    assert "records: 100" in result.stdout
    
    # Verbose context should not appear
    assert "_verbose_source" not in result.stdout
    assert "source:" not in result.stdout
    

def test_warning_shown_at_level_0(run_example_usage):
    """Test that warnings are shown at level 0"""
    result = run_example_usage([])
    
    # Warnings always shown
    assert "Rate limit approaching" in result.stdout
    assert "current_requests: 95" in result.stdout
    assert "limit: 100" in result.stdout


def test_debug_hidden_at_level_0(run_example_usage):
    """Test that debug messages are hidden at level 0"""
    result = run_example_usage([])
    
    # Debug messages should not appear
    assert "Internal state dump" not in result.stdout
    assert "_debug_connections" not in result.stdout


# ============================================================
# Level 1 Tests (-v)
# ============================================================


def test_verbose_context_visible_at_level_1(run_example_usage):
    """Test that _verbose_ context is visible at level 1"""
    result = run_example_usage(["-v"])
    
    # Verbose context should appear
    assert "Processing data" in result.stdout
    assert "source: database.db" in result.stdout
    assert "query: SELECT * FROM users" in result.stdout
    
    assert "Analyzing results" in result.stdout
    assert "processing_time: 0.5s" in result.stdout
    
    # Debug context should NOT appear
    assert "memory_usage:" not in result.stdout
    assert "cache_hits:" not in result.stdout


def test_debug_messages_hidden_at_level_1(run_example_usage):
    """Test that logger.debug() messages are hidden at level 1"""
    result = run_example_usage(["-v"])
    
    # Debug level messages should not appear at level 1
    assert "Internal state dump" not in result.stdout


# ============================================================
# Level 2 Tests (-vv)
# ============================================================


def test_debug_context_visible_at_level_2(run_example_usage):
    """Test that _debug_ context is visible at level 2"""
    result = run_example_usage(["-v", "-v"])
    
    # All context including debug should appear
    assert "Analyzing results" in result.stdout
    assert "processing_time: 0.5s" in result.stdout
    assert "memory_usage: 45MB" in result.stdout
    assert "cache_hits: 42" in result.stdout


def test_debug_messages_visible_at_level_2(run_example_usage):
    """Test that logger.debug() messages are visible at level 2"""
    result = run_example_usage(["-v", "-v"])
    
    # Debug level messages should appear at level 2
    assert "Internal state dump" in result.stdout
    assert "connections: 5" in result.stdout
    assert "queue_size: 12" in result.stdout
    assert "thread_pool: active" in result.stdout


# ============================================================
# General Behavior Tests
# ============================================================


def test_all_examples_complete_successfully(run_example_usage):
    """Test that all examples run without error"""
    result = run_example_usage([])
    
    assert result.returncode == 0
    assert "Example completed" in result.stdout


def test_completion_message_shown(run_example_usage):
    """Test that final success message is shown"""
    result = run_example_usage([])
    
    assert "Operation completed successfully" in result.stdout
    assert "duration: 2.3s" in result.stdout
    assert "items_processed: 100" in result.stdout


def test_all_verbosity_levels_work(run_example_usage):
    """Test that all verbosity levels are accepted"""
    result_0 = run_example_usage([])
    result_1 = run_example_usage(["-v"])
    result_2 = run_example_usage(["-v", "-v"])
    
    assert result_0.returncode == 0
    assert result_1.returncode == 0
    assert result_2.returncode == 0
    
    assert "verbosity level 0" in result_0.stdout
    assert "verbosity level 1" in result_1.stdout
    assert "verbosity level 2" in result_2.stdout
