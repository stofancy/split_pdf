import os
import numpy as np
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io
import fitz  # PyMuPDF
import gc  # For garbage collection
import argparse  # 添加命令行参数支持
from concurrent.futures import ThreadPoolExecutor
import threading

# Increase PIL's maximum image size limit but set a reasonable maximum
Image.MAX_IMAGE_PIXELS = 933120000  # Allows for images up to ~30000x30000 pixels

# 线程本地存储，用于缓存每个线程的PDF writer
thread_local = threading.local()

def get_pdf_writer():
    if not hasattr(thread_local, "pdf_writer"):
        thread_local.pdf_writer = PdfWriter()
    return thread_local.pdf_writer

def parse_arguments():
    parser = argparse.ArgumentParser(description='Split PDF pages vertically into 2 or 3 parts.')
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output PDF file path')
    parser.add_argument('--splits', type=int, choices=[2, 3], default=3,
                       help='Number of parts to split each page into (2 or 3)')
    parser.add_argument('--batch-size', type=int, default=5,
                       help='Number of pages to process in parallel')
    return parser.parse_args()

def find_split_positions(img_array, num_splits):
    """
    查找最佳分割位置,基于图像内容的空白区域
    
    Args:
        img_array: numpy array格式的图像数据
        num_splits: 需要分割的份数(2或3)
    
    Returns:
        分割位置的列表
    """
    # 直接使用numpy数组计算每列的平均亮度
    col_brightness = np.mean(img_array, axis=0)
    
    # 使用滑动窗口平滑亮度值，减少噪声影响
    window_size = 5
    smoothed_brightness = np.convolve(col_brightness, 
                                    np.ones(window_size)/window_size, 
                                    mode='valid')
    
    # 计算理想的分割区间
    width = len(smoothed_brightness)
    segment_width = width // num_splits
    
    # 为每个分割点定义搜索范围
    split_positions = []
    for i in range(1, num_splits):
        target_position = i * segment_width
        search_range = int(segment_width * 0.1)  # 搜索范围为段宽的10%
        start = max(target_position - search_range, 0)
        end = min(target_position + search_range, width)
        
        # 在搜索范围内找到最亮的列
        search_region = smoothed_brightness[start:end]
        max_brightness_idx = np.argmax(search_region)
        split_position = start + max_brightness_idx
        
        split_positions.append(split_position)
    
    return split_positions

def process_section(section, target_width, target_height, dpi):
    """处理单个分割后的区域"""
    # 计算缩放后的尺寸，保持纵横比
    scaled_width = target_width
    scaled_height = int(section.height * target_width / section.width)
    if scaled_height > target_height:
        scaled_height = target_height
        scaled_width = int(section.width * target_height / section.height)
    
    # 创建输出图像并进行缩放
    scaled_section = section.resize(
        (scaled_width, scaled_height),
        Image.Resampling.LANCZOS
    )
    
    # 创建A4页面并居中粘贴
    a4_img = Image.new('RGB', (target_width, target_height), 'white')
    x_offset = (target_width - scaled_width) // 2
    y_offset = (target_height - scaled_height) // 2
    a4_img.paste(scaled_section, (x_offset, y_offset))
    
    # 转换为PDF
    pdf_byte_arr = io.BytesIO()
    a4_img.save(
        pdf_byte_arr,
        format='PDF',
        resolution=dpi,
        save_all=True
    )
    pdf_byte_arr.seek(0)
    
    # 清理内存
    del scaled_section, a4_img
    return pdf_byte_arr

def process_page(args):
    """处理单个PDF页面"""
    page, target_dims, num_splits, dpi = args
    pix = page.get_pixmap(dpi=dpi)
    
    # 转换为numpy数组以提高性能
    img_array = np.frombuffer(pix.samples, dtype=np.uint8)
    img_array = img_array.reshape((pix.height, pix.width, 3))
    
    # 转换为灰度图进行分析
    gray_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    
    # 找到分割位置
    split_positions = find_split_positions(gray_array, num_splits)
    
    # 创建PIL图像用于切割
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    sections = []
    start = 0
    for pos in split_positions:
        sections.append(img.crop((start, 0, pos, img.height)))
        start = pos
    sections.append(img.crop((start, 0, img.width, img.height)))
    
    # 处理每个分割部分
    pdf_sections = []
    for section in sections:
        pdf_byte_arr = process_section(section, *target_dims, dpi)
        pdf_sections.append(pdf_byte_arr)
        del section
    
    # 清理内存
    del img, img_array, gray_array, pix
    gc.collect()
    
    return pdf_sections

def split_pdf(input_path, output_path, num_splits=3, batch_size=5):
    """
    将PDF文档按垂直方向分割成指定数量的部分
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        num_splits: 分割数量(2或3)
        batch_size: 并行处理的页面数量
    """
    # 图像处理常量
    INITIAL_DPI = 250
    TARGET_PPI = 250
    
    # A4尺寸（像素）
    target_width = int(8.27 * TARGET_PPI)
    target_height = int(11.69 * TARGET_PPI)
    target_dims = (target_width, target_height)
    
    # 创建输出PDF
    pdf_writer = PdfWriter()
    doc = fitz.open(input_path)
    
    try:
        # 准备并行处理参数
        page_args = [(doc[i], target_dims, num_splits, INITIAL_DPI) 
                    for i in range(len(doc))]
        
        # 使用线程池并行处理页面
        with ThreadPoolExecutor(max_workers=min(batch_size, os.cpu_count() or 1)) as executor:
            for pdf_sections in executor.map(process_page, page_args):
                for pdf_bytes in pdf_sections:
                    temp_reader = PdfReader(pdf_bytes)
                    pdf_writer.add_page(temp_reader.pages[0])
                    del temp_reader
                    pdf_bytes.close()
    
    finally:
        doc.close()
    
    # 保存输出PDF
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)

def main():
    args = parse_arguments()
    split_pdf(args.input, args.output, args.splits, args.batch_size)

if __name__ == "__main__":
    main()
