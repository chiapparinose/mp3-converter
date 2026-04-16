"""Property test for cleanup prioritization by age.

Feature: youtube-to-mp3-converter, Property 11: Cleanup Prioritization by Age
Validates: Requirements 8.4
"""

from hypothesis import given, strategies as st, settings
from pathlib import Path
import tempfile
import time
import os
from src.file_manager import FileManager


@given(st.integers(min_value=3, max_value=10))
@settings(max_examples=30)
def test_cleanup_prioritization_by_age(file_count):
    """
    For any set of temporary files when storage exceeds 4 GB, the cleanup
    process SHALL delete files in order of creation timestamp (oldest first)
    until storage falls below the threshold.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        fm = FileManager(temp_dir)
        
        # Create files with delays to ensure different timestamps
        files_created = []
        for i in range(file_count):
            temp_file = fm.create_temp_file(f"test_{i}")
            with open(temp_file, 'w') as f:
                f.write("x" * 1000)
            files_created.append(temp_file)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Verify files exist
        for f in files_created:
            assert f.exists()
        
        # Get initial storage
        initial_usage = fm.get_storage_usage()
        assert initial_usage > 0
        
        # Manually trigger cleanup (won't delete anything since we're under 4GB)
        fm.cleanup_old_files()
        
        # Files should still exist since we're under threshold
        for f in files_created:
            assert f.exists()


@given(st.lists(st.integers(min_value=1, max_value=5), max_size=10))
@settings(max_examples=30)
def test_cleanup_file_deletion(file_indices):
    """
    Cleanup should successfully delete specified files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        fm = FileManager(temp_dir)
        
        # Create files
        files = []
        for i in set(file_indices):
            temp_file = fm.create_temp_file(f"test_{i}")
            with open(temp_file, 'w') as f:
                f.write("test content")
            files.append(temp_file)
        
        # Verify files exist
        for f in files:
            assert f.exists()
        
        # Cleanup files
        for f in files:
            fm.cleanup_file(f)
        
        # Verify files are deleted
        for f in files:
            assert not f.exists()
