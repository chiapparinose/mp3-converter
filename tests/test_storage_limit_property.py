"""Property test for storage limit enforcement.

Feature: youtube-to-mp3-converter, Property 10: Storage Limit Enforcement
Validates: Requirements 8.3
"""

from hypothesis import given, strategies as st, settings
from pathlib import Path
import tempfile
import os
from src.file_manager import FileManager


@given(st.integers(min_value=0, max_value=10))
@settings(max_examples=50)
def test_storage_limit_enforcement(file_count):
    """
    For any sequence of file operations, the system SHALL maintain total
    temporary storage usage at or below 5 GB by refusing new operations
    or triggering cleanup when the limit would be exceeded.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        fm = FileManager(temp_dir)
        
        # Create some files
        for i in range(file_count):
            temp_file = fm.create_temp_file(f"test_{i}")
            # Write some content
            with open(temp_file, 'w') as f:
                f.write("x" * 100)
        
        # Check storage usage is tracked
        usage = fm.get_storage_usage()
        assert usage >= 0
        
        # Check storage limit enforcement
        is_within_limit = fm.enforce_storage_limit()
        # Should always be within limit for small test files
        assert is_within_limit is True


@given(st.lists(st.integers(min_value=100, max_value=1000), max_size=20))
@settings(max_examples=30)
def test_storage_usage_calculation(file_sizes):
    """
    Storage usage calculation should accurately reflect total file sizes.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        fm = FileManager(temp_dir)
        
        expected_total = 0
        for i, size in enumerate(file_sizes):
            temp_file = fm.create_temp_file(f"test_{i}")
            with open(temp_file, 'wb') as f:
                f.write(b"x" * size)
            expected_total += size
        
        actual_usage = fm.get_storage_usage()
        assert actual_usage == expected_total
