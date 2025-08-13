# Usage Guide

This guide covers common usage patterns and examples for the Kobo API Python Client.

## Basic Setup

### Authentication

The client supports multiple ways to provide authentication credentials:

#### Method 1: Direct Parameters

```python
from kobo_api import KoboClient

client = KoboClient(
    server_url="https://kobo.example.com",
    token="your-api-token"
)
```

#### Method 2: Environment Variables

Set environment variables and initialize without parameters:

```python
import os

# Set environment variables
os.environ['URL'] = "https://kobo.example.com"
os.environ['TOKEN'] = "your-api-token"

# Initialize client (will read from environment)
client = KoboClient()
```

#### Method 3: .env File

Create a `.env` file in your working directory:

```env
URL=https://kobo.example.com
TOKEN=your-api-token
```

Then initialize the client:

```python
from kobo_api import KoboClient

# Will automatically read from .env file
client = KoboClient()
```

### Client Configuration

You can configure caching and other options:

```python
client = KoboClient(
    server_url="https://kobo.example.com",
    token="your-api-token",
    cache=True,           # Enable response caching (default)
    cache_ttl=3600       # Cache TTL in seconds (default: 36000)
)
```

## Common Operations

### Connection Testing

Always test your connection first:

```python
if client.ping():
    print("Successfully connected to KoBoToolbox")
else:
    print("Failed to connect - check your credentials and URL")
```

### Working with Assets (Forms)

#### List All Assets

```python
# Get all assets/forms
assets = client.get_assets()

for asset in assets:
    print(f"Name: {asset['name']}")
    print(f"ID: {asset['uid']}")
    print(f"Asset Type: {asset.get('asset_type', 'N/A')}")
    print("---")
```

#### Get Specific Asset

```python
# Get details for a specific asset
asset_id = "your-asset-id"
asset = client.get_asset(asset_id)

print(f"Asset name: {asset['name']}")
print(f"Created: {asset['date_created']}")
print(f"Owner: {asset['owner__username']}")
```

### Working with Form Data

#### Get Form Submissions

```python
# Get all submissions for a form
asset_id = "your-asset-id"
data = client.get_asset_data(asset_id)

print(f"Total submissions: {data.get('count', 0)}")

# Iterate through submissions
for submission in data.get('results', []):
    print(f"Submission ID: {submission['_id']}")
    print(f"Submitted: {submission['_submission_time']}")
    # Access form fields directly
    # print(f"Field value: {submission.get('field_name')}")
```

#### Filtered Data Retrieval

```python
# Get data with query parameters
data = client.get_asset_data(
    asset_id,
    limit=100,                    # Limit number of results
    offset=0,                     # Skip first N results
    sort='{"_submission_time": 1}', # Sort by submission time
    fields='["field1", "field2"]'   # Only include specific fields
)
```

## Advanced Usage

### Cache Management

```python
# Clear the cache when needed
client.clear_cache()

# Disable cache for sensitive operations
client_no_cache = KoboClient(
    server_url="https://kobo.example.com",
    token="your-api-token",
    cache=False
)
```

### Error Handling

```python
import requests

try:
    assets = client.get_assets()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - check your token")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error: {e}")
except requests.RequestException as e:
    print(f"Network error: {e}")
```

### Batch Operations

```python
# Process multiple assets efficiently
assets = client.get_assets()

for asset in assets:
    try:
        # Get data for each asset
        data = client.get_asset_data(asset['uid'], limit=10)
        print(f"{asset['name']}: {data.get('count', 0)} submissions")
    except requests.HTTPError as e:
        print(f"Failed to get data for {asset['name']}: {e}")
```

## Performance Tips

1. **Use caching**: Enable caching for read-heavy operations (enabled by default)
2. **Limit results**: Use `limit` parameter to avoid downloading large datasets
3. **Specific fields**: Use `fields` parameter to only retrieve needed data
4. **Connection reuse**: Reuse the same client instance for multiple requests

## Best Practices

1. **Environment variables**: Store credentials in environment variables, not in code
2. **Error handling**: Always wrap API calls in try-catch blocks
3. **Rate limiting**: Be mindful of API rate limits in production
4. **Data validation**: Validate form data before processing
5. **Logging**: Use logging to track API usage and debug issues

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The client uses loguru for internal logging
# Set appropriate log levels for debugging
```