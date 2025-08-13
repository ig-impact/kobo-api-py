from unittest.mock import patch

from kobo_api import KoboClient


class TestEnvPrecedence:
    @patch("kobo_api.kobo_client.dotenv_values")
    def test_explicit_params_override_env(self, mock_dotenv):
        mock_dotenv.return_value = {
            "URL": "https://env.example.com",
            "TOKEN": "env_token",
        }

        client = KoboClient(
            server_url="https://arg.example.com",
            token="arg_token",
            cache=False,
        )

        assert client.server_url == "https://arg.example.com"
        assert client.token == "arg_token"

    @patch("kobo_api.kobo_client.dotenv_values")
    def test_uses_env_when_args_missing(self, mock_dotenv):
        mock_dotenv.return_value = {
            "URL": "https://env.example.com",
            "TOKEN": "env_token",
        }

        client = KoboClient(cache=False)
        assert client.server_url == "https://env.example.com"
        assert client.token == "env_token"
