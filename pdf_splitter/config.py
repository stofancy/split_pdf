# PDF and Image Processing Configuration
class Config:
    # Image processing constants
    INITIAL_DPI = 250
    TARGET_PPI = 250
    
    # Maximum image size limit
    MAX_IMAGE_PIXELS = 933120000  # Allows for images up to ~30000x30000 pixels
    
    @classmethod
    def get_target_dimensions(cls):
        """Get A4 dimensions in pixels based on target PPI"""
        target_width = int(8.27 * cls.TARGET_PPI)
        target_height = int(11.69 * cls.TARGET_PPI)
        return target_width, target_height
