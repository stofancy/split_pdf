import argparse
from .pdf_processor import PDFProcessor

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Split PDF pages vertically into 2 or 3 parts.')
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output PDF file path')
    parser.add_argument(
        '--splits', 
        type=int, 
        choices=[2, 3], 
        default=3,
        help='Number of parts to split each page into (2 or 3)'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=5,
        help='Number of pages to process in parallel'
    )
    return parser.parse_args()

def main():
    """Main entry point for the CLI"""
    args = parse_arguments()
    processor = PDFProcessor()
    processor.split_pdf(args.input, args.output, args.splits, args.batch_size)
    args = parse_arguments()
    processor = PDFProcessor()
    processor.split_pdf(args.input, args.output, args.splits, args.batch_size)

if __name__ == "__main__":
    main()
