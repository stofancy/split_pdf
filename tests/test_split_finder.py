import pytest
import numpy as np
from pdf_splitter.split_finder import SplitFinder

@pytest.fixture
def sample_array():
    """Create a sample array for testing splits"""
    # Create a 1000x800 array with some content
    array = np.ones((1000, 800)) * 255  # White background
    
    # Add some "text" blocks
    array[100:200, 100:700] = 0  # Black text in first third
    array[400:500, 100:700] = 0  # Black text in middle
    array[700:800, 100:700] = 0  # Black text in last third
    
    return array

def test_find_split_positions_2_splits(sample_array):
    """Test finding 2 split positions"""
    positions = SplitFinder.find_split_positions(sample_array, 2)
    
    assert len(positions) == 1  # Should return one split position for 2 splits
    assert 0 < positions[0] < sample_array.shape[1]  # Split should be within image bounds

def test_find_split_positions_3_splits(sample_array):
    """Test finding 3 split positions"""
    positions = SplitFinder.find_split_positions(sample_array, 3)
    
    assert len(positions) == 2  # Should return two split positions for 3 splits
    assert all(0 < pos < sample_array.shape[1] for pos in positions)  # All splits within bounds
    assert positions[0] < positions[1]  # Positions should be in ascending order

def test_empty_image():
    """Test splitting completely white image"""
    white_image = np.ones((1000, 800)) * 255
    positions = SplitFinder.find_split_positions(white_image, 2)
    assert len(positions) == 1  # Should still find a split position
    # The actual position might vary based on implementation

def test_dense_content():
    """Test splitting image with dense content"""
    dense_array = np.zeros((1000, 800))  # All black
    positions = SplitFinder.find_split_positions(dense_array, 3)
    assert len(positions) == 2
    assert positions[0] < positions[1]  # Positions should be ordered

@pytest.mark.parametrize("splits,expected_sections", [
    (2, 2),
    (3, 3),
])
def test_split_sections_count(sample_array, splits, expected_sections):
    """Test that correct number of sections are created"""
    positions = SplitFinder.find_split_positions(sample_array, splits)
    assert len(positions) == splits - 1

def test_consistent_splits():
    """Test that split positions are consistent for same input"""
    array = np.random.rand(1000, 800)
    splits1 = SplitFinder.find_split_positions(array, 2)
    splits2 = SplitFinder.find_split_positions(array, 2)
    assert np.array_equal(splits1, splits2)