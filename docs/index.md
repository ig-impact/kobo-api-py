# Kobo API Python Client

A Python wrapper for the KoBoToolbox API v2 that provides easy access to KoBoToolbox data and form management.

## Overview

This library provides a simple interface to interact with KoBoToolbox forms and data through their REST API. KoBoToolbox is an open-source tool for designing, collecting, and analyzing data in humanitarian contexts.

## Quick Install

Install the package from PyPI:

```bash
pip install kobo-api-py
```

For development with all extras:

```bash
pip install -e .[dev,docs]
```

## Quick Start

```python
from kobo_api import KoboClient

# Initialize client with server URL and token
client = KoboClient(
    server_url="https://kobo.example.com",
    token="your-api-token"
)

# Check if the server is reachable
if client.ping():
    print("Connected to KoBoToolbox!")

# Get all assets (forms)
assets = client.get_assets()
for asset in assets:
    print(f"Form: {asset['name']} (ID: {asset['uid']})")

# Get data from a specific form
if assets:
    asset_id = assets[0]['uid']
    data = client.get_asset_data(asset_id)
    print(f"Form has {data.get('count', 0)} submissions")
```

## Features

- Simple authentication with server URL and token
- Configurable request caching for better performance
- Built-in retry logic for reliable API calls
- Support for all major KoBoToolbox API v2 endpoints
- Type hints for better development experience

## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [Usage Guide](usage.md) - Examples and common patterns
- [API Reference](api.md) - Complete API documentation