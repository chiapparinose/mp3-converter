"""Property test for progress tracking monotonicity.

Feature: youtube-to-mp3-converter, Property 6: Progress Tracking Monotonicity
Validates: Requirements 5.1, 5.2, 5.4
"""

from hypothesis import given, strategies as st, settings, stateful
from src.progress_tracker import ProgressTracker
from src.models import Stage


# Strategy for generating progress values
progress_values = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Strategy for generating stages
stages = st.sampled_from([
    Stage.VALIDATION,
    Stage.DOWNLOAD,
    Stage.CONVERSION,
    Stage.METADATA,
    Stage.DELIVERY,
])


@given(stages_list=st.lists(st.tuples(stages, progress_values), min_size=2, max_size=20))
@settings(max_examples=50)
def test_progress_monotonicity(stages_list):
    """
    For any conversion process, the reported progress percentage SHALL be
    monotonically non-decreasing throughout all stages and SHALL reach
    exactly 100% upon successful completion.
    """
    tracker = ProgressTracker()
    
    # Track overall progress history
    progress_history = []
    
    # Track max progress per stage to ensure we don't go backwards within a stage
    stage_max_progress = {}
    
    for stage, progress in stages_list:
        # Only update if progress is >= current max for this stage
        current_max = stage_max_progress.get(stage, 0.0)
        if progress >= current_max:
            stage_max_progress[stage] = progress
            tracker.update_stage(stage, progress)
            overall = tracker.get_overall_progress()
            progress_history.append(overall)
    
    # Verify monotonicity (non-decreasing)
    for i in range(1, len(progress_history)):
        # Allow small floating point tolerance
        assert progress_history[i] >= progress_history[i-1] - 0.001, \
            f"Progress decreased: {progress_history[i-1]} -> {progress_history[i]}"


@given(progress=progress_values)
@settings(max_examples=30)
def test_progress_never_decreases_for_same_stage(progress):
    """
    Progress for the same stage should never decrease.
    """
    tracker = ProgressTracker()
    
    tracker.update_stage(Stage.DOWNLOAD, progress)
    first_overall = tracker.get_overall_progress()
    
    # Update with same or higher progress
    tracker.update_stage(Stage.DOWNLOAD, max(progress, 0.5))
    second_overall = tracker.get_overall_progress()
    
    assert second_overall >= first_overall


@given(final_progress=progress_values)
@settings(max_examples=30)
def test_progress_reaches_100_on_completion(final_progress):
    """
    When all stages complete, progress should reach 100%.
    """
    tracker = ProgressTracker()
    
    # Complete all stages
    tracker.update_stage(Stage.VALIDATION, 1.0)
    tracker.update_stage(Stage.DOWNLOAD, 1.0)
    tracker.update_stage(Stage.CONVERSION, 1.0)
    tracker.update_stage(Stage.METADATA, 1.0)
    tracker.update_stage(Stage.DELIVERY, 1.0)
    
    overall = tracker.get_overall_progress()
    assert abs(overall - 1.0) < 0.001, f"Expected 1.0, got {overall}"


@given(
    validation_progress=progress_values,
    download_progress=progress_values,
    conversion_progress=progress_values
)
@settings(max_examples=30)
def test_weighted_progress_calculation(validation_progress, download_progress, conversion_progress):
    """
    Overall progress should be weighted sum of stage progress.
    """
    tracker = ProgressTracker()
    
    tracker.update_stage(Stage.VALIDATION, validation_progress)
    tracker.update_stage(Stage.DOWNLOAD, download_progress)
    tracker.update_stage(Stage.CONVERSION, conversion_progress)
    
    overall = tracker.get_overall_progress()
    
    # Expected: validation*0.05 + download*0.50 + conversion*0.35
    expected = (
        validation_progress * 0.05 +
        download_progress * 0.50 +
        conversion_progress * 0.35
    )
    
    assert abs(overall - expected) < 0.001
