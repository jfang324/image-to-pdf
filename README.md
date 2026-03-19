# image-to-pdf

A Python TUI application for converting images to PDF files.

## Features

- Select images from any directory via a three-panel interface
- Reorder images before converting
- Configurable PDF quality and optimization
- Exportable library functions for programmatic use

## Requirements

- Python 3.9, 3.10, 3.11, or 3.12

## Installation

```sh
git clone https://github.com/jfang324/image-to-pdf.git
cd image-to-pdf
pip install .
```

## Usage

Run the application:

```sh
image-to-pdf
```

### Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `-q, --quality` | PDF quality 1-100 (higher = larger file) | 75 |
| `-o, --optimize` | Optimize PDF file size | false |

Example:

```sh
image-to-pdf --quality 90 --optimize
```

## Programmatic Use

```python
from image_to_pdf import convert_images_to_pdf, is_image

# Check if a file is an image
is_image("photo.jpg")  # True or False

# Convert images to PDF
convert_images_to_pdf(
    ["photo1.jpg", "photo2.png"],
    "/output/directory",
    "my_report",
    quality=75,
    optimize=False,
)
```

## Development

### Setup

Install with dev dependencies:

```sh
poetry install --with dev
```

### Pre-commit Hooks

Install pre-commit to run linting and type-checking on every commit:

```sh
pip install pre-commit
pre-commit install
```

### Textual Dev Tools

The `textual` CLI is installed as part of the dev dependencies. Run it with:

```sh
poetry run textual --help
```

To run the app with live-reload and the dev console:

```sh
poetry run textual run --dev image_to_pdf.app:ImageToPDFApp
```

To pass CLI arguments, use `--` to separate Textual flags from app flags:

```sh
poetry run textual run --dev image_to_pdf.app:ImageToPDFApp -- --quality 90 --optimize
```

### Running Tests

```sh
pytest
```

With coverage:

```sh
coverage run -m pytest
coverage report -m
```

### Linting and Type-Checking

```sh
ruff check .
ruff format --check .
pyright
```

## Contact

Jeffery Fang - jefferyfang324@gmail.com

## Tools

- [Python](https://www.python.org/) - Language
- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [Textual](https://textual.textualize.io/) - TUI framework
- [Poetry](https://python-poetry.org/) - Dependency management
- [Ruff](https://docs.astral.sh/ruff/) - Linting and formatting
- [Pyright](https://github.com/microsoft/pyright) - Static type checking
- [pytest](https://docs.pytest.org/) - Testing
- [coverage](https://coverage.readthedocs.io/) - Code coverage
