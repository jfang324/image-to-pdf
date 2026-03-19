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

On Windows, curses is required:

```sh
pip install windows-curses
```

Or install with Poetry for automatic Windows curses handling:

```sh
poetry install --with windows
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
poetry run textual run --dev -m image_to_pdf.app
```

Note: Poetry 2.0 removed `poetry shell`. To activate the virtual environment in your shell:

```sh
eval "$(poetry env activate)"
```

Or run commands directly with `poetry run`.

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

## Tools

- [Python](https://www.python.org/) - Language
- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [Textual](https://textual.textualize.io/) - TUI framework
- [Poetry](https://python-poetry.org/) - Dependency management
- [Ruff](https://docs.astral.sh/ruff/) - Linting and formatting
- [Pyright](https://github.com/microsoft/pyright) - Static type checking
- [pytest](https://docs.pytest.org/) - Testing
- [coverage](https://coverage.readthedocs.io/) - Code coverage
