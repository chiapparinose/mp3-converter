"""Unit tests for ProgressTracker component."""

import pytest
import threading
import time
from src.progress_tracker import ProgressTracker
from src.models import Stage, ProgressUpdate


class TestProgressTracker:
    """Tests for ProgressTracker class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker()
    
    def test_initial_state(self):
        """Test initial state of progress tracker."""
        assert self.tracker.get_current_stage() == Stage.VALIDATION
        assert self.tracker.get_overall_progress() == 0.0
    
    def test_update_stage(self):
        """Test updating stage progress."""
        self.tracker.update_stage(Stage.VALIDATION, 0.5)
        
        assert self.tracker.get_current_stage() == Stage.VALIDATION
    
    def test_update_multiple_stages(self):
        """Test updating multiple stages."""
        self.tracker.update_stage(Stage.VALIDATION, 1.0)
        self.tracker.update_stage(Stage.DOWNLOAD, 0.5)
        
        # Overall progress should be weighted
        overall = self.tracker.get_overall_progress()
        assert 0 < overall < 1
    
    def test_overall_progress_calculation(self):
        """Test weighted overall progress calculation."""
        # Complete validation (5%)
        self.tracker.update_stage(Stage.VALIDATION, 1.0)
        assert abs(self.tracker.get_overall_progress() - 0.05) < 0.01
        
        # Complete download (50%)
        self.tracker.update_stage(Stage.DOWNLOAD, 1.0)
        assert abs(self.tracker.get_overall_progress() - 0.55) < 0.01
        
        # Complete conversion (35%)
        self.tracker.update_stage(Stage.CONVERSION, 1.0)
        assert abs(self.tracker.get_overall_progress() - 0.90) < 0.01
        
        # Complete metadata (5%)
        self.tracker.update_stage(Stage.METADATA, 1.0)
        assert abs(self.tracker.get_overall_progress() - 0.95) < 0.01
        
        # Complete delivery (5%)
        self.tracker.update_stage(Stage.DELIVERY, 1.0)
        assert abs(self.tracker.get_overall_progress() - 1.0) < 0.01
    
    def test_progress_clamping(self):
        """Test that progress is clamped to 0.0-1.0 range."""
        self.tracker.update_stage(Stage.VALIDATION, 1.5)
        # Should be clamped to 1.0
        overall = self.tracker.get_overall_progress()
        assert overall <= 1.0
        
        self.tracker.update_stage(Stage.DOWNLOAD, -0.5)
        # Should be clamped to 0.0
        overall = self.tracker.get_overall_progress()
        assert overall >= 0.0
    
    def test_subscribe_callback(self):
        """Test subscriber callback mechanism."""
        received_updates = []
        
        def callback(update: ProgressUpdate):
            received_updates.append(update)
        
        self.tracker.subscribe(callback)
        self.tracker.update_stage(Stage.VALIDATION, 0.5)
        
        assert len(received_updates) == 1
        assert received_updates[0].stage == Stage.VALIDATION
        assert received_updates[0].stage_progress == 0.5
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers receive updates."""
        updates1 = []
        updates2 = []
        
        self.tracker.subscribe(lambda u: updates1.append(u))
        self.tracker.subscribe(lambda u: updates2.append(u))
        
        self.tracker.update_stage(Stage.DOWNLOAD, 0.3)
        
        assert len(updates1) == 1
        assert len(updates2) == 1
    
    def test_thread_safety(self):
        """Test thread-safe progress updates."""
        errors = []
        
        def update_progress(stage, progress):
            try:
                for _ in range(100):
                    self.tracker.update_stage(stage, progress)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=update_progress, args=(Stage.DOWNLOAD, 0.5)),
            threading.Thread(target=update_progress, args=(Stage.CONVERSION, 0.3)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_reset(self):
        """Test resetting progress tracker."""
        self.tracker.update_stage(Stage.VALIDATION, 1.0)
        self.tracker.update_stage(Stage.DOWNLOAD, 0.5)
        
        self.tracker.reset()
        
        assert self.tracker.get_current_stage() == Stage.VALIDATION
        assert self.tracker.get_overall_progress() == 0.0
    
    def test_progress_history(self):
        """Test progress history tracking."""
        self.tracker.update_stage(Stage.VALIDATION, 0.5)
        self.tracker.update_stage(Stage.VALIDATION, 1.0)
        
        history = self.tracker.get_progress_history()
        assert len(history) == 2
