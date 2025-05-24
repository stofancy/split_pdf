from PIL import Image
import io
from .config import Config

class ImageProcessor:
    @staticmethod
    def process_section(section: Image.Image, target_width: int, target_height: int, dpi: int) -> io.BytesIO:
        """Process a single split section and convert to PDF"""
        # Calculate scaled dimensions maintaining aspect ratio
        scaled_width = target_width
        scaled_height = int(section.height * target_width / section.width)
        if scaled_height > target_height:
            scaled_height = target_height
            scaled_width = int(section.width * target_height / section.height)
        
        # Scale the section
        scaled_section = section.resize(
            (scaled_width, scaled_height),
            Image.Resampling.LANCZOS
        )
        
        # Create A4 page and center the content
        a4_img = Image.new('RGB', (target_width, target_height), 'white')
        x_offset = (target_width - scaled_width) // 2
        y_offset = (target_height - scaled_height) // 2
        a4_img.paste(scaled_section, (x_offset, y_offset))
        
        # Convert to PDF
        pdf_byte_arr = io.BytesIO()
        a4_img.save(
            pdf_byte_arr,
            format='PDF',
            resolution=dpi,
            save_all=True
        )
        pdf_byte_arr.seek(0)
        
        # Clean up
        del scaled_section, a4_img
        return pdf_byte_arr

    @staticmethod
    def init_image_settings():
        """Initialize PIL image settings"""
        Image.MAX_IMAGE_PIXELS = Config.MAX_IMAGE_PIXELS
