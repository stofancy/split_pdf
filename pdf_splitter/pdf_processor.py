import os
import threading
import gc
import numpy as np
from PIL import Image
import fitz
from PyPDF2 import PdfReader, PdfWriter
from concurrent.futures import ThreadPoolExecutor
from .split_finder import SplitFinder
from .image_processor import ImageProcessor
from .config import Config

class PDFProcessor:
    def __init__(self):
        self.thread_local = threading.local()
        ImageProcessor.init_image_settings()
    
    def get_pdf_writer(self):
        """Get thread-local PDF writer instance"""
        if not hasattr(self.thread_local, "pdf_writer"):
            self.thread_local.pdf_writer = PdfWriter()
        return self.thread_local.pdf_writer

    def process_page(self, args):
        """Process a single PDF page"""
        page, target_dims, num_splits, dpi = args
        pix = page.get_pixmap(dpi=dpi)
        
        # Convert to numpy array for performance
        img_array = np.frombuffer(pix.samples, dtype=np.uint8)
        img_array = img_array.reshape((pix.height, pix.width, 3))
        
        # Convert to grayscale for analysis
        gray_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        
        # Find split positions
        split_positions = SplitFinder.find_split_positions(gray_array, num_splits)
        
        # Create PIL image for splitting
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Split into sections
        sections = []
        start = 0
        for pos in split_positions:
            sections.append(img.crop((start, 0, pos, img.height)))
            start = pos
        sections.append(img.crop((start, 0, img.width, img.height)))
        
        # Process each section
        pdf_sections = []
        for section in sections:
            pdf_byte_arr = ImageProcessor.process_section(section, *target_dims, dpi)
            pdf_sections.append(pdf_byte_arr)
            del section
        
        # Clean up
        del img, img_array, gray_array, pix
        gc.collect()
        
        return pdf_sections

    def split_pdf(self, input_path: str, output_path: str, num_splits: int = 3, batch_size: int = 5):
        """
        Split PDF document vertically into specified number of parts
        
        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            num_splits: Number of parts to split into (2 or 3)
            batch_size: Number of pages to process in parallel
        """
        target_dims = Config.get_target_dimensions()
        
        # Create output PDF
        pdf_writer = PdfWriter()
        doc = fitz.open(input_path)
        
        try:
            # Prepare parallel processing parameters
            page_args = [
                (doc[i], target_dims, num_splits, Config.INITIAL_DPI) 
                for i in range(len(doc))
            ]
            
            # Process pages in parallel using thread pool
            with ThreadPoolExecutor(max_workers=min(batch_size, os.cpu_count() or 1)) as executor:
                for pdf_sections in executor.map(self.process_page, page_args):
                    for pdf_bytes in pdf_sections:
                        temp_reader = PdfReader(pdf_bytes)
                        pdf_writer.add_page(temp_reader.pages[0])
                        del temp_reader
                        pdf_bytes.close()
        
        finally:
            doc.close()
        
        # Save output PDF
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
