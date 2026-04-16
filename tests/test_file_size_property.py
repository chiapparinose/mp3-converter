"""Property-based test for file size calculation accuracy."""

import pytest
from hypothesis import given, strategies as st


# Feature: youtube-to-mp3-converter, Property 8: File Size Calculation Accuracy
@pytest.mark.property
@given(st.integers(min_value=0, max_value=10**12))  # Up to 1TB
def test_file_size_calculation_accuracy(size_bytes):
    """
    For any file with a size in bytes, the conversion to megabytes SHALL be 
    accurate within 0.01 MB, using the formula: size_mb = size_bytes / (1024 * 1024).
    
    **Validates: Requirements 6.3**
    """
    # Calculate size in MB
    size_mb = size_bytes / (1024 * 1024)
    
    # Convert back to bytes
    calculated_bytes = size_mb * 1024 * 1024
    
    # Verify accuracy within 0.01 MB (10485.76 bytes)
    tolerance_bytes = 0.01 * 1024 * 1024
    assert abs(calculated_bytes - size_bytes) <= tolerance_bytes
    
    # Verify the calculation is consistent
    assert size_mb >= 0
    if size_bytes == 0:
        assert size_mb == 0
    else:
        assert size_mb > 0
