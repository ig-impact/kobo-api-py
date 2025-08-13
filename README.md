# Kobo API Python Client

[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://ig-impact.github.io/kobo-api-py/)

A Python wrapper for the KoBoToolbox API v2 that provides easy access to KoBoToolbox data and form management.

## Quick Start

Install the package:

```bash
pip install kobo-api-py
```

Basic usage:

```python
from kobo_api import KoboClient

# Initialize client
client = KoboClient(
    server_url="https://kobo.example.com",
    token="your-api-token"
)

# Test connection
if client.ping():
    print("Connected!")

# Get all forms
assets = client.get_assets()
for asset in assets:
    print(f"Form: {asset['name']}")

# Get form data
if assets:
    data = client.get_asset_data(assets[0]['uid'])
    print(f"Submissions: {data.get('count', 0)}")
```

For development installation with documentation building:

```bash
pip install -e .[docs]
```

## Documentation

Complete documentation is available at: https://ig-impact.github.io/kobo-api-py/

The documentation includes:

- [Installation Guide](https://ig-impact.github.io/kobo-api-py/installation/) - Detailed setup instructions
- [Usage Guide](https://ig-impact.github.io/kobo-api-py/usage/) - Examples and common patterns  
- [API Reference](https://ig-impact.github.io/kobo-api-py/api/) - Complete API documentation

## Features

- Simple authentication with server URL and token
- Configurable request caching for better performance
- Built-in retry logic for reliable API calls
- Support for KoBoToolbox API v2 endpoints
- Type hints for better development experience

## Requirements

- Python 3.10 or higher
- Active KoBoToolbox instance
- Valid API token

## Contributing

See the [documentation](https://ig-impact.github.io/kobo-api-py/installation/#development-installation) for development setup instructions.
