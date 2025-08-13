# Installation

## Standard Installation

Install the package from PyPI using pip:

```bash
pip install kobo-api-py
```

## Optional Extras

The package includes optional dependency groups for different use cases:

### Development Dependencies

For contributing to the project or running tests:

```bash
pip install kobo-api-py[dev]
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `responses` - HTTP response mocking
- `requests-mock` - Request mocking

### Documentation Dependencies

For building and serving the documentation:

```bash
pip install kobo-api-py[docs]
```

This includes:
- `mkdocs` - Documentation generator
- `mkdocs-material` - Material Design theme
- `mkdocstrings` - API documentation from docstrings
- Additional MkDocs plugins

### All Dependencies

To install everything (useful for development):

```bash
pip install kobo-api-py[dev,docs]
```

## Development Installation

If you want to contribute to the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/ig-impact/kobo-api-py.git
   cd kobo-api-py
   ```

2. Install in editable mode with development dependencies:
   ```bash
   pip install -e .[dev]
   ```

3. Run the tests to verify installation:
   ```bash
   pytest
   ```

## Environment Setup

The library supports configuration through environment variables. Create a `.env` file in your project root:

```env
URL=https://your-kobo-instance.com
TOKEN=your-api-token
```

Or set environment variables directly:

```bash
export URL="https://your-kobo-instance.com"
export TOKEN="your-api-token"
```

## Requirements

- Python 3.10 or higher
- Active KoBoToolbox instance
- Valid API token

## Troubleshooting

### Connection Issues

If you're having trouble connecting:

1. Verify your server URL is correct (should not end with `/`)
2. Check that your API token is valid
3. Ensure your KoBoToolbox instance supports API v2
4. Test the connection manually using `client.ping()`

### Import Errors

If you get import errors:

1. Ensure the package is installed: `pip list | grep kobo-api-py`
2. Try reinstalling: `pip uninstall kobo-api-py && pip install kobo-api-py`
3. Check your Python version: `python --version`