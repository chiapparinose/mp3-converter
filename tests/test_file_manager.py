"""Unit tests for FileManager component."""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.file_manager import FileManager


class TestFileManager:
    """Test suite for FileManager class."""
    
    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        # Create a temporary directory for testing
        self.test_temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(temp_dir=self.test_temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove the temporary directory after tests
        if Path(self.test_temp_dir).exists():
            shutil.rmtree(self.test_temp_dir)
    
    def test_create_temp_file_creates_file(self):
        """Test that create_temp_file creates a file."""
        file_path = self.file_manager.create_temp_file("test")
        
        assert file_path.exists()
        assert file_path.is_file()
    
    def test_create_temp_file_with_prefix(self):
        """Test that create_temp_file uses the provided prefix."""
        prefix = "audio"
        file_path = self.file_manager.create_temp_file(prefix)
        
        assert file_path.name.startswith(prefix)
    
    def test_create_temp_file_unique_identifiers(self):
        """Test that create_temp_file generates unique identifiers."""
        file1 = self.file_manager.create_temp_file("test")
        file2 = self.file_manager.create_temp_file("test")
        
        assert file1 != file2
        assert file1.name != file2.name
    
    def test_create_temp_file_in_temp_directory(self):
        """Test that create_temp_file creates files in the temp directory."""
        file_path = self.file_manager.create_temp_file("test")
        
        assert file_path.parent == Path(self.test_temp_dir)
    
    def test_sanitize_filename_removes_less_than(self):
        """Test that sanitize_filename removes < character."""
        filename = "test<file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert "<" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_greater_than(self):
        """Test that sanitize_filename removes > character."""
        filename = "test>file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert ">" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_colon(self):
        """Test that sanitize_filename removes : character."""
        filename = "test:file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert ":" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_double_quote(self):
        """Test that sanitize_filename removes \" character."""
        filename = 'test"file.mp3'
        sanitized = FileManager.sanitize_filename(filename)
        
        assert '"' not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_forward_slash(self):
        """Test that sanitize_filename removes / character."""
        filename = "test/file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert "/" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_backslash(self):
        """Test that sanitize_filename removes \\ character."""
        filename = "test\\file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert "\\" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_pipe(self):
        """Test that sanitize_filename removes | character."""
        filename = "test|file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert "|" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_question_mark(self):
        """Test that sanitize_filename removes ? character."""
        filename = "test?file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert "?" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_asterisk(self):
        """Test that sanitize_filename removes * character."""
        filename = "test*file.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert "*" not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_removes_all_invalid_chars(self):
        """Test that sanitize_filename removes all invalid characters at once."""
        filename = '<test>:file"/\\|?*.mp3'
        sanitized = FileManager.sanitize_filename(filename)
        
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            assert char not in sanitized
        assert sanitized == "testfile.mp3"
    
    def test_sanitize_filename_preserves_valid_chars(self):
        """Test that sanitize_filename preserves valid characters."""
        filename = "test_file-123.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert sanitized == "test_file-123.mp3"
    
    def test_sanitize_filename_preserves_spaces(self):
        """Test that sanitize_filename preserves spaces."""
        filename = "test file name.mp3"
        sanitized = FileManager.sanitize_filename(filename)
        
        assert sanitized == "test file name.mp3"
    
    def test_sanitize_filename_empty_string(self):
        """Test that sanitize_filename handles empty string."""
        filename = ""
        sanitized = FileManager.sanitize_filename(filename)
        
        assert sanitized == ""
    
    def test_sanitize_filename_only_invalid_chars(self):
        """Test that sanitize_filename handles string with only invalid characters."""
        filename = '<>:"/\\|?*'
        sanitized = FileManager.sanitize_filename(filename)
        
        assert sanitized == ""
    
    def test_get_storage_usage_empty_directory(self):
        """Test that get_storage_usage returns 0 for empty directory."""
        usage = self.file_manager.get_storage_usage()
        
        assert usage == 0
    
    def test_get_storage_usage_single_file(self):
        """Test that get_storage_usage calculates size for single file."""
        # Create a file with known content
        file_path = self.file_manager.create_temp_file("test")
        test_content = b"Hello, World!"
        file_path.write_bytes(test_content)
        
        usage = self.file_manager.get_storage_usage()
        
        assert usage == len(test_content)
    
    def test_get_storage_usage_multiple_files(self):
        """Test that get_storage_usage calculates total size for multiple files."""
        # Create multiple files with known content
        file1 = self.file_manager.create_temp_file("test1")
        file2 = self.file_manager.create_temp_file("test2")
        
        content1 = b"Hello"
        content2 = b"World!"
        
        file1.write_bytes(content1)
        file2.write_bytes(content2)
        
        usage = self.file_manager.get_storage_usage()
        
        assert usage == len(content1) + len(content2)
    
    def test_get_storage_usage_ignores_subdirectories(self):
        """Test that get_storage_usage only counts files, not directories."""
        # Create a subdirectory
        subdir = Path(self.test_temp_dir) / "subdir"
        subdir.mkdir()
        
        # Create a file in the subdirectory
        file_in_subdir = subdir / "test.txt"
        content = b"Test content"
        file_in_subdir.write_bytes(content)
        
        usage = self.file_manager.get_storage_usage()
        
        # Should include the file in the subdirectory
        assert usage == len(content)
    
    def test_get_storage_usage_after_file_deletion(self):
        """Test that get_storage_usage updates after file deletion."""
        # Create a file
        file_path = self.file_manager.create_temp_file("test")
        content = b"Test content"
        file_path.write_bytes(content)
        
        # Verify initial usage
        usage_before = self.file_manager.get_storage_usage()
        assert usage_before == len(content)
        
        # Delete the file
        file_path.unlink()
        
        # Verify usage is now 0
        usage_after = self.file_manager.get_storage_usage()
        assert usage_after == 0
    
    def test_temp_directory_created_on_init(self):
        """Test that FileManager creates temp directory if it doesn't exist."""
        # Create a new temp directory path that doesn't exist
        new_temp_dir = Path(self.test_temp_dir) / "new_temp"
        
        # Ensure it doesn't exist
        assert not new_temp_dir.exists()
        
        # Create FileManager with this path
        fm = FileManager(temp_dir=str(new_temp_dir))
        
        # Verify directory was created
        assert new_temp_dir.exists()
        assert new_temp_dir.is_dir()
        
        # Clean up
        shutil.rmtree(new_temp_dir)
    
    def test_cleanup_file_deletes_file(self):
        """Test that cleanup_file deletes the specified file."""
        # Create a file
        file_path = self.file_manager.create_temp_file("test")
        file_path.write_bytes(b"test content")
        
        assert file_path.exists()
        
        # Cleanup the file
        self.file_manager.cleanup_file(file_path)
        
        # File should be deleted
        assert not file_path.exists()
    
    def test_cleanup_file_nonexistent_file(self):
        """Test that cleanup_file handles nonexistent file gracefully."""
        nonexistent = Path(self.test_temp_dir) / "nonexistent.txt"
        
        # Should not raise exception
        self.file_manager.cleanup_file(nonexistent)
    
    def test_cleanup_old_files_under_threshold(self):
        """Test that cleanup_old_files does nothing when under threshold."""
        # Create a small file
        file_path = self.file_manager.create_temp_file("test")
        file_path.write_bytes(b"small content")
        
        # Cleanup should not delete anything
        self.file_manager.cleanup_old_files()
        
        # File should still exist
        assert file_path.exists()
    
    def test_enforce_storage_limit_under_limit(self):
        """Test enforce_storage_limit returns True when under limit."""
        # Create a small file
        file_path = self.file_manager.create_temp_file("test")
        file_path.write_bytes(b"small content")
        
        # Should be under limit
        assert self.file_manager.enforce_storage_limit() is True
    
    def test_enforce_storage_limit_empty_directory(self):
        """Test enforce_storage_limit returns True for empty directory."""
        assert self.file_manager.enforce_storage_limit() is True
