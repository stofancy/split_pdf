import os
import pytest
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image
import fitz
from io import BytesIO
from pdf_splitter.pdf_processor import PDFProcessor
from pdf_splitter.config import Config

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF file for testing"""
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size
    page.insert_text((100, 100), "Test content")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_init():
    """Test PDFProcessor initialization"""
    processor = PDFProcessor()
    assert hasattr(processor, 'thread_local')

def test_get_pdf_writer():
    """Test get_pdf_writer creates new instance if not exists"""
    processor = PDFProcessor()
    writer1 = processor.get_pdf_writer()
    writer2 = processor.get_pdf_writer()
    assert writer1 is writer2  # Should return same instance for same thread

@pytest.mark.parametrize("num_splits", [2, 3])
def test_split_pdf_creates_output(pdf_processor, sample_pdf, tmp_path, num_splits):
    """Test that split_pdf creates an output file with correct number of pages"""
    output_path = tmp_path / "output.pdf"
    pdf_processor.split_pdf(sample_pdf, str(output_path), num_splits=num_splits)
    
    assert output_path.exists()
    with fitz.open(str(output_path)) as doc:
        # Original page should be split into num_splits parts
        assert len(doc) == num_splits

def test_process_page(pdf_processor, sample_pdf):
    """Test process_page method"""
    with fitz.open(sample_pdf) as doc:
        page = doc[0]
        target_dims = Config.get_target_dimensions()
        args = (page, target_dims, 2, Config.INITIAL_DPI)
        
        # Process the page
        sections = pdf_processor.process_page(args)
        
        # Verify we got correct number of sections
        assert len(sections) == 2
        
        # Each section should be a BytesIO object containing PDF data
        for section in sections:
            assert isinstance(section, BytesIO)

@pytest.mark.parametrize("batch_size", [1, 2, 5])
def test_split_pdf_batch_processing(pdf_processor, sample_pdf, tmp_path, batch_size):
    """Test that split_pdf handles different batch sizes correctly"""
    output_path = tmp_path / "output.pdf"
    pdf_processor.split_pdf(sample_pdf, str(output_path), batch_size=batch_size)
    assert output_path.exists()

def test_split_pdf_error_handling(pdf_processor, tmp_path):
    """Test split_pdf handles missing input file correctly"""
    non_existent_file = tmp_path / "nonexistent.pdf"
    output_path = tmp_path / "output.pdf"
    
    with pytest.raises(Exception):
        pdf_processor.split_pdf(str(non_existent_file), str(output_path))