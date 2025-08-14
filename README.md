# kobo-api-py

[![License](https://img.shields.io/github/license/ig-impact/kobo-api-py.svg)](LICENSE)
[![Test Status](https://github.com/ig-impact/kobo-api-py/actions/workflows/python-package.yml/badge.svg)](https://github.com/ig-impact/kobo-api-py/actions/workflows/python-package.yml)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

A Python client for interacting with the KoboToolbox  V2 API, providing convenient methods for retrieving, submitting, and managing KoboToolbox project and form data.

---

## Installation

This package is not available on PyPI.

Clone the repository and install locally:

```bash
git clone https://github.com/ig-impact/kobo-api-py.git
cd kobo-api-py
pip install -r requirements.txt
```

---

## Usage

You can use the `KoboClient` class to interact with the KoboToolbox API. You must provide your server URL and API token via arguments or a `.env` file.

```python
from kobo_api import KoboClient

client = KoboClient(
    server_url="https://kf.kobotoolbox.org",  # or your custom server
    token="YOUR_API_TOKEN"
)

# Example: ping the server
if client.ping():
    print("KoboToolbox server is reachable!")

# Example: fetch assets (forms)
assets = client.get_assets()
print(assets)
```

You can also use a `.env` file in your project root:

```sh
URL=https://kf.kobotoolbox.org
TOKEN=YOUR_API_TOKEN
```

---

## Contributing

Contributions are welcome! Please open an issue or pull request.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

> For the latest code and more usage examples, see the [repository on GitHub](https://github.com/ig-impact/kobo-api-py).
