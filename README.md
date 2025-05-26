# PDF Page Splitter

A smart Windows application for splitting scanned PDF pages vertically into 2 or 3 parts. Perfect for scanned books or documents where multiple pages were scanned onto a single page. Features intelligent content detection to preserve the natural flow of text and images.

## Key Features

- Smart content detection to avoid cutting through text or images
- Automatically excludes blank areas at top/bottom/left/right
- Preserves connected content blocks
- Ignores isolated content far from main text
- Optimized for scanned books and documents
- Fast parallel processing for multi-page documents

## Quick Start

1. Download `pdf_splitter.exe` from the [Releases](https://github.com/stofancy/split_pdf/releases/latest) page
2. Simply drag and drop your PDF file onto the `pdf_splitter.exe` icon
3. The split PDF will be automatically created in the same folder as your original PDF

For example, if you drag `book.pdf` onto the executable, it will create `book_split.pdf` in the same folder.

## Advanced Usage

You can also run the executable from the command line for more control:

```powershell
pdf_splitter.exe input.pdf output.pdf [--splits 2|3] [--batch-size NUMBER]
```

Options:
- `--splits`: Number of parts to split into (2 or 3, default: 3)
- `--batch-size`: Pages to process in parallel (default: 5)

## Common Questions

### How does it choose where to split?
The application uses smart content detection to:
1. Analyze the content distribution on each page
2. Find natural gaps between content blocks
3. Avoid cutting through text or images
4. Maintain the logical flow of content

### What output format will I get?
- Output files are optimized for A4 size
- Each section is properly aligned and scaled
- Blank margins are automatically trimmed
- File name format: `original_name_split.pdf`

### System Requirements
- Windows 7/8/10/11
- No additional software needed
- Minimum 4GB RAM recommended for large PDFs

## Need Help?

If you encounter any issues:
1. Make sure your PDF is readable and not password-protected
2. Try using the command-line interface for more control
3. Report issues on our [GitHub Issues](https://github.com/stofancy/split_pdf/issues) page

## License

This project is licensed under the MIT License. The LICENSE file is included in the package.

## Processing Notes
- Progress will be shown during processing
- Large PDF files may take some time to process

## Releases

Releases are managed through GitHub Releases. Each release includes:
- Windows executable (`pdf_splitter.exe`)
- Source code (zip and tar.gz)
- Release notes describing changes

To download the latest release:
1. Go to the [Releases page](https://github.com/stofancy/split_pdf/releases)
2. Download `pdf_splitter.exe` from the latest release
3. Run the executable directly - no installation needed

For developers:
- Release versions follow [Semantic Versioning](https://semver.org/)
- Each release is tagged in the repository
- Release artifacts are built using PyInstaller with our custom spec file
