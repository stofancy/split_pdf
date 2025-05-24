# PDF Page Splitter

This Windows application allows you to split PDF pages vertically into 2 or 3 parts. It's particularly useful for scanned books or documents where multiple pages were scanned onto a single page.

## Installation

### Option 1: Using the Executable (Recommended)

1. Download `pdf_splitter.exe` from the [Releases](../../releases) page
2. No additional installation needed - just run the executable
3. No Python or other dependencies required

### Option 2: Running from Source

If you want to run from source or develop the application:

1. Prerequisites:
   - Python 3.7 or higher (Download from https://www.python.org/downloads/)
   - pip (usually comes with Python)

2. Installation:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   pip install -r requirements.txt
   ```

## Usage

### Using the Executable

1. **Command Line Interface**:
   ```bash
   pdf_splitter.exe input.pdf output.pdf [--splits 2|3] [--batch-size NUMBER]
   ```

   Options:
   - `--splits`: Number of parts to split each page into (2 or 3, default is 3)
   - `--batch-size`: Number of pages to process in parallel (default is 5)

2. **Drag and Drop**:
   - Simply drag your PDF file onto `pdf_splitter.exe`
   - It will create an output file with "_split" added to the name

### Using from Source

If running from source:
```bash
python split_pdf.py input.pdf output.pdf [--splits 2|3] [--batch-size NUMBER]
```

## Examples

1. Split a PDF into 3 parts (default):
   ```bash
   pdf_splitter.exe input.pdf output.pdf
   ```

2. Split into 2 parts:
   ```bash
   pdf_splitter.exe input.pdf output.pdf --splits 2
   ```

3. Split into 3 parts with faster processing:
   ```bash
   pdf_splitter.exe input.pdf output.pdf --splits 3 --batch-size 10
   ```

## Building from Source

To create your own executable:

1. Clone the repository
2. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
3. Build the executable:
   ```bash
   pyinstaller --onefile split_pdf.py --name pdf_splitter
   ```
   
The executable will be created in the `dist` folder.

## Notes

- The application will automatically detect the best splitting positions based on the content of each page
- The output PDF will be optimized for A4 size
- Progress will be shown during processing
- Large PDF files may take some time to process
