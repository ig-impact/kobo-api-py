from unittest.mock import Mock, patch

import pytest
import requests

from kobo_api import KoboClient


class TestInternalGet:
    def test__get_builds_url_and_passes_kwargs(self):
        with patch.object(KoboClient, "_make_session") as mock_make_sess:
            mock_session = Mock()
            mock_resp = Mock()
            mock_resp.json.return_value = {"ok": True}
            mock_session.get.return_value = mock_resp
            mock_make_sess.return_value = mock_session

            client = KoboClient(server_url="https://test.com", token="t", cache=False)
            res = client._get("api/v2/assets", params={"limit": 10}, timeout=5)

            assert res == {"ok": True}
            mock_session.get.assert_called_once_with(
                "https://test.com/api/v2/assets",
                params={"limit": 10},
                timeout=5,
            )

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("api/v2/assets", "https://test.com/api/v2/assets"),
            ("/api/v2/assets", "https://test.com/api/v2/assets"),
            ("api/v2/assets/", "https://test.com/api/v2/assets/"),
            ("/api/v2/assets/?a=1", "https://test.com/api/v2/assets/?a=1"),
        ],
    )
    def test__get_url_variations(self, path: str, expected):
        with patch.object(KoboClient, "_make_session") as mock_make_sess:
            mock_session = Mock()
            mock_resp = Mock()
            mock_resp.json.return_value = {"ok": True}
            mock_session.get.return_value = mock_resp
            mock_make_sess.return_value = mock_session

            client = KoboClient(server_url="https://test.com/", token="t", cache=False)
            client._get(path)

            mock_session.get.assert_called_once_with(expected)

    def test__get_raises_http_error(self):
        with patch.object(KoboClient, "_make_session") as mock_make_sess:
            mock_session = Mock()
            mock_resp = Mock()
            mock_resp.raise_for_status.side_effect = requests.HTTPError("boom")
            mock_session.get.return_value = mock_resp
            mock_make_sess.return_value = mock_session

            client = KoboClient(server_url="https://test.com", token="t", cache=False)
            with pytest.raises(requests.HTTPError):
                client._get("api/v2/assets")
