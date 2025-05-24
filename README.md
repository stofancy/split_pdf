# PDF Page Splitter

This Windows application allows you to split PDF pages vertically into 2 or 3 parts. It's particularly useful for scanned books or documents where multiple pages were scanned onto a single page.

## Prerequisites

- Windows operating system
- Python 3.7 or higher (Download from https://www.python.org/downloads/)
- pip (usually comes with Python)

## Installation

No installation is needed. Just download all the files and keep them in the same folder:
- split_pdf.bat
- split_pdf.py
- requirements.txt

When you run the application for the first time, it will automatically install the required Python packages.

## Usage

You can use the application in two ways:

1. **Drag and Drop**: Simply drag a PDF file onto the `split_pdf.bat` file.

2. **Command Line**:
   Open a command prompt in the application folder and run:
   ```
   split_pdf.bat input.pdf output.pdf [--splits 2|3] [--batch-size 5]
   ```

   Options:
   - `--splits`: Number of parts to split each page into (2 or 3, default is 3)
   - `--batch-size`: Number of pages to process in parallel (default is 5)

## Examples

1. Split pages into 3 parts:
   ```
   split_pdf.bat input.pdf output.pdf --splits 3
   ```

2. Split pages into 2 parts with increased batch size:
   ```
   split_pdf.bat input.pdf output.pdf --splits 2 --batch-size 10
   ```

## Notes

- The application will automatically detect the best splitting positions based on the content of each page
- The output PDF will be optimized for A4 size
- Progress will be shown during processing
- Large PDF files may take some time to process
