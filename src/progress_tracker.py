"""Progress tracking component for conversion pipeline."""

import threading
from typing import Callable, Optional, List
from datetime import timedelta
from .models import Stage, ProgressUpdate


class ProgressTracker:
    """Tracks and reports progress across pipeline stages."""
    
    # Weight distribution for overall progress
    STAGE_WEIGHTS = {
        Stage.VALIDATION: 0.05,
        Stage.DOWNLOAD: 0.50,
        Stage.CONVERSION: 0.35,
        Stage.METADATA: 0.05,
        Stage.DELIVERY: 0.05,
    }
    
    def __init__(self):
        """Initialize ProgressTracker."""
        self._stage_progress = {stage: 0.0 for stage in Stage if stage not in [Stage.ERROR, Stage.CLEANUP]}
        self._current_stage = Stage.VALIDATION
        self._subscribers: List[Callable[[ProgressUpdate], None]] = []
        self._lock = threading.Lock()
        self._progress_history: List[float] = []  # Track progress for monotonicity
    
    def update_stage(self, stage: Stage, progress: float) -> None:
        """
        Update progress for a specific stage.
        
        Args:
            stage: The pipeline stage
            progress: Progress value (0.0 to 1.0)
        """
        with self._lock:
            self._current_stage = stage
            if stage in self._stage_progress:
                self._stage_progress[stage] = max(0.0, min(1.0, progress))
            
            overall = self.get_overall_progress()
            self._progress_history.append(overall)
            
            # Notify subscribers
            update = ProgressUpdate(
                stage=stage,
                stage_progress=progress,
                overall_progress=overall,
                estimated_time_remaining=None,
                message=f"{stage.value}: {progress * 100:.1f}%"
            )
            
            for callback in self._subscribers:
                try:
                    callback(update)
                except Exception:
                    pass
    
    def get_overall_progress(self) -> float:
        """
        Get weighted overall progress.
        
        Returns:
            Overall progress (0.0 to 1.0)
        """
        total = 0.0
        for stage, weight in self.STAGE_WEIGHTS.items():
            total += self._stage_progress.get(stage, 0.0) * weight
        return min(1.0, total)
    
    def get_current_stage(self) -> Stage:
        """
        Get current pipeline stage.
        
        Returns:
            Current Stage
        """
        return self._current_stage
    
    def subscribe(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """
        Subscribe to progress updates.
        
        Args:
            callback: Function to call on progress updates
        """
        self._subscribers.append(callback)
    
    def get_progress_history(self) -> List[float]:
        """Get history of overall progress values."""
        return self._progress_history.copy()
    
    def reset(self) -> None:
        """Reset progress tracker for new conversion."""
        with self._lock:
            self._stage_progress = {stage: 0.0 for stage in Stage if stage not in [Stage.ERROR, Stage.CLEANUP]}
            self._current_stage = Stage.VALIDATION
            self._progress_history = []
