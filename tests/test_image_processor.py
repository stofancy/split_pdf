import pytest
import numpy as np
from PIL import Image
from io import BytesIO
from pdf_splitter.image_processor import ImageProcessor

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    width, height = 600, 800
    image = Image.new('RGB', (width, height), 'white')
    # Add some text/content to the image
    draw = Image.new('RGB', (400, 600), 'black')
    image.paste(draw, (100, 100))
    return image

def test_init_image_settings():
    """Test initialization of image settings"""
    ImageProcessor.init_image_settings()
    assert Image.MAX_IMAGE_PIXELS is None  # Verify the setting was changed

def test_process_section_group(sample_image):
    """Test processing of multiple sections with actual content"""
    # Create test sections with actual content
    sections = [
        sample_image.crop((0, 0, 300, 800)),
        sample_image.crop((300, 0, 600, 800))
    ]
    
    # Process sections
    target_width, target_height = 300, 800
    dpi = 300
    results = ImageProcessor.process_section_group(sections, target_width, target_height, dpi)
    
    # Verify results
    assert len(results) == len(sections)
    for result in results:
        assert isinstance(result, BytesIO)
        # Verify it contains PDF data
        assert result.getvalue().startswith(b'%PDF')