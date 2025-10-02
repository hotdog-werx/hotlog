"""Tests for example_prefixes.py"""


# ============================================================
# Level 0 Tests (Default)
# ============================================================


def test_basic_prefix_filtering_level_0(run_example_prefixes):
    """Test that _verbose_ and _debug_ prefixes are filtered at level 0"""
    result = run_example_prefixes([])
    
    # Base context should appear
    assert "Processing dataset" in result.stdout
    assert "records: 1000" in result.stdout
    
    # Verbose context should NOT appear
    assert "_verbose_source" not in result.stdout
    assert "source:" not in result.stdout
    assert "format:" not in result.stdout
    
    # Debug context should NOT appear
    assert "_debug_file_size" not in result.stdout
    assert "file_size:" not in result.stdout


def test_tool_execution_formatting_level_0(run_example_prefixes):
    """Test that tool execution uses custom 'pkg' prefix at level 0"""
    result = run_example_prefixes([])
    
    # Should show tool execution with custom prefix
    assert "pkg[ruff-format]" in result.stdout
    assert "ruff format --line-length=80 ." in result.stdout
    
    assert "pkg[pytest]" in result.stdout
    assert "pytest tests/ -v" in result.stdout
    
    # Verbose/debug context should not appear
    assert "_verbose_files_changed" not in result.stdout
    assert "_debug_config" not in result.stdout


def test_database_query_level_0(run_example_prefixes):
    """Test database query formatting at level 0"""
    result = run_example_prefixes([])
    
    # Base context shown
    assert "Database query completed" in result.stdout
    assert "duration: 150ms" in result.stdout
    assert "rows_affected: 42" in result.stdout
    
    # Verbose/debug context hidden
    assert "query:" not in result.stdout
    assert "connection:" not in result.stdout
    assert "query_plan:" not in result.stdout


# ============================================================
# Level 1 Tests (-v)
# ============================================================


def test_verbose_prefix_visible_at_level_1(run_example_prefixes):
    """Test that _verbose_ prefixed context is visible at level 1"""
    result = run_example_prefixes(["-v"])
    
    # Base context
    assert "Processing dataset" in result.stdout
    assert "records: 1000" in result.stdout
    
    # Verbose context should appear
    assert "source: data.csv" in result.stdout
    assert "format: CSV" in result.stdout
    
    # Debug context should NOT appear
    assert "file_size:" not in result.stdout
    assert "encoding:" not in result.stdout


def test_tool_verbose_context_level_1(run_example_prefixes):
    """Test that tool execution shows verbose context at level 1"""
    result = run_example_prefixes(["-v"])
    
    # Tool execution with verbose details
    assert "pkg[ruff-format]" in result.stdout
    assert "files_changed: 14" in result.stdout
    
    assert "pkg[pytest]" in result.stdout
    assert "tests_passed: 95" in result.stdout
    assert "tests_failed: 5" in result.stdout
    
    # Debug details should not appear
    assert "config:" not in result.stdout
    assert "duration:" not in result.stdout or "duration: 150ms" in result.stdout  # duration is base context in query example


def test_database_query_level_1(run_example_prefixes):
    """Test database query shows verbose context at level 1"""
    result = run_example_prefixes(["-v"])
    
    # Base and verbose context
    assert "Database query completed" in result.stdout
    assert "duration: 150ms" in result.stdout
    assert "query: SELECT * FROM users" in result.stdout
    assert "connection: localhost:5432" in result.stdout
    
    # Debug context hidden
    assert "query_plan:" not in result.stdout
    assert "cache_hit:" not in result.stdout


# ============================================================
# Level 2 Tests (-vv)
# ============================================================


def test_debug_prefix_visible_at_level_2(run_example_prefixes):
    """Test that _debug_ prefixed context is visible at level 2"""
    result = run_example_prefixes(["-v", "-v"])
    
    # All context should appear
    assert "Processing dataset" in result.stdout
    assert "records: 1000" in result.stdout
    assert "source: data.csv" in result.stdout
    assert "format: CSV" in result.stdout
    assert "file_size: 2.5MB" in result.stdout
    assert "encoding: utf-8" in result.stdout


def test_tool_debug_context_level_2(run_example_prefixes):
    """Test that tool execution shows debug context at level 2"""
    result = run_example_prefixes(["-v", "-v"])
    
    # Tool execution with all details
    assert "pkg[ruff-format]" in result.stdout
    assert "files_changed: 14" in result.stdout
    assert "config: .ruff.toml" in result.stdout
    
    assert "pkg[pytest]" in result.stdout
    assert "tests_passed: 95" in result.stdout
    assert "tests_failed: 5" in result.stdout
    assert "duration: 5.2s" in result.stdout


def test_database_query_level_2(run_example_prefixes):
    """Test database query shows debug context at level 2"""
    result = run_example_prefixes(["-v", "-v"])
    
    # All context visible
    assert "Database query completed" in result.stdout
    assert "query: SELECT * FROM users" in result.stdout
    assert "connection: localhost:5432" in result.stdout
    assert "query_plan: Sequential Scan" in result.stdout
    assert "cache_hit: true" in result.stdout


# ============================================================
# General Behavior Tests
# ============================================================


def test_custom_prefix_in_summary(run_example_prefixes):
    """Test that summary mentions custom 'pkg' prefix"""
    result = run_example_prefixes([])
    
    assert result.returncode == 0
    assert "Summary" in result.stdout
    assert "pkg" in result.stdout.lower()


def test_tool_execution_without_tool_name(run_example_prefixes):
    """Test tool execution works without explicit tool name"""
    result = run_example_prefixes([])
    
    # Should still show the command even without tool name
    assert "python setup.py build" in result.stdout


def test_all_verbosity_levels_complete(run_example_prefixes):
    """Test that example completes at all verbosity levels"""
    result_0 = run_example_prefixes([])
    result_1 = run_example_prefixes(["-v"])
    result_2 = run_example_prefixes(["-v", "-v"])
    
    assert result_0.returncode == 0
    assert result_1.returncode == 0
    assert result_2.returncode == 0
    
    assert "verbosity level: 0" in result_0.stdout
    assert "verbosity level: 1" in result_1.stdout
    assert "verbosity level: 2" in result_2.stdout
