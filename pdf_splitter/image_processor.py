from PIL import Image
import io
import numpy as np
from .config import Config

class ImageProcessor:
    @staticmethod
    def process_section(section: Image.Image, target_width: int, target_height: int, dpi: int) -> io.BytesIO:
        """Process a single split section and convert to PDF"""
        # Convert to grayscale numpy array for analysis
        img_array = np.array(section)
        if len(img_array.shape) == 3:
            gray_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        else:
            gray_array = img_array
            
        # Find content boundaries
        content_bbox = ImageProcessor.find_content_bounds(gray_array)
        if content_bbox is None:
            # If no content found, create empty page
            a4_img = Image.new('RGB', (target_width, target_height), 'white')
        else:
            # Crop to content area
            section = section.crop(content_bbox)
              # Add moderate margins (3%)
            margin = int(min(target_width, target_height) * 0.03)
            max_width = target_width - (2 * margin)
            max_height = target_height - (2 * margin)
            
            # Scale maintaining aspect ratio
            scale = min(max_width / section.width, max_height / section.height)
            new_width = int(section.width * scale)
            new_height = int(section.height * scale)
            
            # Resize section
            section = section.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center on page
            a4_img = Image.new('RGB', (target_width, target_height), 'white')
            x = (target_width - new_width) // 2
            y = (target_height - new_height) // 2
            a4_img.paste(section, (x, y))
        
        # Convert to PDF
        pdf_bytes = io.BytesIO()
        a4_img.save(pdf_bytes, format='PDF', resolution=dpi, save_all=True)
        pdf_bytes.seek(0)
        return pdf_bytes

    @staticmethod
    def init_image_settings():
        """Initialize PIL image settings for optimal performance"""
        Image.MAX_IMAGE_PIXELS = None
        pass

    @staticmethod
    def find_content_bounds(gray_array: np.ndarray, threshold: int = 250) -> tuple:
        """Find content boundaries excluding blank spaces around the edges"""
        height, width = gray_array.shape
        
        # Calculate density for rows and columns
        row_density = np.sum(gray_array < threshold, axis=1) / width
        col_density = np.sum(gray_array < threshold, axis=0) / height
          # Use moderate threshold to better identify blank areas
        density_threshold = 0.01  # 1% threshold for blank space
        
        # Find content boundaries with smoothing to avoid noise
        smooth_window = 5  # pixels
        row_density_smooth = np.convolve(row_density, np.ones(smooth_window)/smooth_window, mode='same')
        col_density_smooth = np.convolve(col_density, np.ones(smooth_window)/smooth_window, mode='same')
        
        # Find content boundaries
        content_rows = np.where(row_density_smooth > density_threshold)[0]
        content_cols = np.where(col_density_smooth > density_threshold)[0]
        
        if len(content_rows) == 0 or len(content_cols) == 0:
            return None
            
        # Get boundaries
        top = content_rows[0]
        bottom = content_rows[-1]
        left = content_cols[0]
        right = content_cols[-1]
        
        return (left, top, right, bottom)
