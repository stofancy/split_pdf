from PIL import Image
import io
import numpy as np
from .config import Config

class ImageProcessor:
    @staticmethod
    def init_image_settings():
        """Initialize PIL image settings for optimal performance"""
        Image.MAX_IMAGE_PIXELS = None
        pass

    @staticmethod
    def find_content_blocks(gray_array: np.ndarray, threshold: int = 250) -> list:
        """Find content blocks in a grayscale image"""
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
        
        # Find potential content blocks
        content_rows = np.where(row_density_smooth > density_threshold)[0]
        content_cols = np.where(col_density_smooth > density_threshold)[0]
        
        if len(content_rows) == 0 or len(content_cols) == 0:
            return []

        # Analyze gaps between content rows
        row_gaps = np.diff(content_rows)
        gap_threshold = 50  # Minimum gap to consider content as separated
        big_gaps = np.where(row_gaps > gap_threshold)[0]
        
        # If no big gaps, treat as single connected block
        if len(big_gaps) == 0:
            # Return single block with connected flag
            return [{
                'bbox': (content_cols[0], content_rows[0], 
                        content_cols[-1], content_rows[-1]),
                'area': (content_cols[-1] - content_cols[0]) * 
                       (content_rows[-1] - content_rows[0]),
                'content_pixels': np.sum(gray_array[content_rows[0]:content_rows[-1]+1,
                                                  content_cols[0]:content_cols[-1]+1] < threshold),
                'center': ((content_cols[0] + content_cols[-1]) / 2,
                         (content_rows[0] + content_rows[-1]) / 2),
                'connected': True
            }]
            
        # Process multiple blocks if gaps exist
        block_starts = np.concatenate(([0], big_gaps + 1))
        block_ends = np.concatenate((big_gaps, [len(content_rows) - 1]))
        
        blocks = []
        for start_idx, end_idx in zip(block_starts, block_ends):
            top = content_rows[start_idx]
            bottom = content_rows[end_idx]
            
            # Find columns with content
            block_cols = col_density_smooth[top:bottom+1]
            col_indices = np.where(block_cols > density_threshold)[0]
            if len(col_indices) == 0:
                continue
                
            left = content_cols[0]
            right = content_cols[-1]
            
            width = right - left
            height = bottom - top
            area = width * height
            if area == 0:
                continue
                
            content_pixels = np.sum(gray_array[top:bottom+1, left:right+1] < threshold)
            if content_pixels < 100:  # Minimum content threshold
                continue
                
            blocks.append({
                'bbox': (left, top, right, bottom),
                'area': area,
                'content_pixels': content_pixels,
                'center': ((left + right) / 2, (top + bottom) / 2),
                'connected': False
            })
        
        return blocks

    @staticmethod
    def analyze_section_group(sections):
        """Analyze a group of sections to find the one with isolated corner content"""
        section_blocks = []
        has_connected_content = False
        
        # Analyze each section
        for i, section in enumerate(sections):
            gray_array = np.array(section)
            if len(gray_array.shape) == 3:
                gray_array = np.dot(gray_array[...,:3], [0.2989, 0.5870, 0.1140])
            
            blocks = ImageProcessor.find_content_blocks(gray_array)
            if not blocks:
                continue
                
            # Check for connected content
            if any(block.get('connected', False) for block in blocks):
                has_connected_content = True
                break
                
            # Add section index to blocks
            for block in blocks:
                block['section_index'] = i
            section_blocks.extend(blocks)
        
        if has_connected_content or not section_blocks:
            return None
        
        # Find main content block
        section_blocks.sort(key=lambda b: b['content_pixels'], reverse=True)
        main_block = section_blocks[0]
        main_center = main_block['center']
        
        # Calculate isolation scores
        max_distance = 0
        farthest_section = 0
        
        for block in section_blocks[1:]:
            center = block['center']
            dx = center[0] - main_center[0]
            dy = center[1] - main_center[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance > max_distance:
                max_distance = distance
                farthest_section = block['section_index']
        
        return {
            'main_section': main_block['section_index'],
            'farthest_section': farthest_section,
            'distance_threshold': max_distance * 0.75  # 75% of max distance
        }

    @staticmethod
    def process_section_group(sections, target_width: int, target_height: int, dpi: int) -> list:
        """Process a group of sections from the same page"""
        if not sections:
            return []
            
        # Analyze section group
        analysis = ImageProcessor.analyze_section_group(sections)
        
        # Process each section
        pdf_sections = []
        for i, section in enumerate(sections):
            img_array = np.array(section)
            if len(img_array.shape) == 3:
                gray_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
            else:
                gray_array = img_array
            
            blocks = ImageProcessor.find_content_blocks(gray_array)
            
            # Skip filtering if no analysis or connected content
            if not blocks or not analysis or any(b.get('connected', False) for b in blocks):
                if not blocks:
                    pdf_bytes = ImageProcessor.create_blank_page(target_width, target_height, dpi)
                else:
                    # Use full content area
                    left = min(b['bbox'][0] for b in blocks)
                    top = min(b['bbox'][1] for b in blocks)
                    right = max(b['bbox'][2] for b in blocks)
                    bottom = max(b['bbox'][3] for b in blocks)
                    crop_box = (left, top, right, bottom)
                    pdf_bytes = ImageProcessor.create_page_with_content(
                        section.crop(crop_box), target_width, target_height, dpi)
            else:
                # Filter blocks in the section with farthest content
                if i == analysis['farthest_section']:
                    filtered_blocks = []
                    for block in blocks:
                        # Only exclude very small and distant blocks
                        if block['content_pixels'] > main_block['content_pixels'] * 0.1:
                            filtered_blocks.append(block)
                    blocks = filtered_blocks if filtered_blocks else blocks
                
                # Calculate boundaries from remaining blocks
                left = min(b['bbox'][0] for b in blocks)
                top = min(b['bbox'][1] for b in blocks)
                right = max(b['bbox'][2] for b in blocks)
                bottom = max(b['bbox'][3] for b in blocks)
                crop_box = (left, top, right, bottom)
                pdf_bytes = ImageProcessor.create_page_with_content(
                    section.crop(crop_box), target_width, target_height, dpi)
            
            pdf_sections.append(pdf_bytes)
        
        return pdf_sections

    @staticmethod
    def create_blank_page(width: int, height: int, dpi: int) -> io.BytesIO:
        """Create a blank PDF page"""
        img = Image.new('RGB', (width, height), 'white')
        pdf_bytes = io.BytesIO()
        img.save(pdf_bytes, format='PDF', resolution=dpi, save_all=True)
        pdf_bytes.seek(0)
        return pdf_bytes

    @staticmethod
    def create_page_with_content(section: Image.Image, target_width: int, target_height: int, dpi: int) -> io.BytesIO:
        """Create a PDF page with the given content section"""
        # Add margins (3%)
        margin = int(min(target_width, target_height) * 0.03)
        max_width = target_width - (2 * margin)
        max_height = target_height - (2 * margin)
        
        # Scale maintaining aspect ratio
        scale = min(max_width / section.width, max_height / section.height)
        new_width = int(section.width * scale)
        new_height = int(section.height * scale)
        
        # Resize and center
        section = section.resize((new_width, new_height), Image.Resampling.LANCZOS)
        a4_img = Image.new('RGB', (target_width, target_height), 'white')
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        a4_img.paste(section, (x, y))
        
        # Convert to PDF
        pdf_bytes = io.BytesIO()
        a4_img.save(pdf_bytes, format='PDF', resolution=dpi, save_all=True)
        pdf_bytes.seek(0)
        return pdf_bytes
