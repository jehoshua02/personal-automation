import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from oauth import OAuthClient, SCOPES


@pytest.fixture
def client_config():
    return {
        "web": {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/callback"],
        }
    }


@pytest.fixture
def oauth_client(client_config, tmp_path):
    config_path = tmp_path / "client_secret.json"
    config_path.write_text(json.dumps(client_config))
    token_path = tmp_path / "token.json"
    return OAuthClient(str(config_path), str(token_path))


class TestBuildAuthUrl:
    def test_includes_client_id(self, oauth_client):
        url = oauth_client.build_auth_url()
        assert "client_id=test-client-id" in url

    def test_includes_redirect_uri(self, oauth_client):
        url = oauth_client.build_auth_url()
        assert "redirect_uri=" in url
        assert "localhost" in url

    def test_includes_all_scopes(self, oauth_client):
        url = oauth_client.build_auth_url()
        for scope in SCOPES:
            assert scope.replace(":", "%3A").replace("/", "%2F") in url or scope in url

    def test_requests_offline_access(self, oauth_client):
        url = oauth_client.build_auth_url()
        assert "access_type=offline" in url


class TestExchangeCode:
    @patch("oauth.requests.post")
    def test_sends_correct_params(self, mock_post, oauth_client):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "access123",
                "refresh_token": "refresh123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
        oauth_client.exchange_code("auth-code-123")
        call_data = mock_post.call_args[1]["data"]
        assert call_data["code"] == "auth-code-123"
        assert call_data["client_id"] == "test-client-id"
        assert call_data["client_secret"] == "test-client-secret"
        assert call_data["grant_type"] == "authorization_code"

    @patch("oauth.requests.post")
    def test_stores_token(self, mock_post, oauth_client):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "access123",
                "refresh_token": "refresh123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
        oauth_client.exchange_code("auth-code-123")
        assert os.path.exists(oauth_client.token_path)
        with open(oauth_client.token_path) as f:
            token = json.load(f)
        assert token["access_token"] == "access123"
        assert token["refresh_token"] == "refresh123"

    @patch("oauth.requests.post")
    def test_raises_on_error(self, mock_post, oauth_client):
        mock_post.return_value = MagicMock(
            status_code=400,
            text="Bad Request",
            json=lambda: {"error": "invalid_grant"},
        )
        with pytest.raises(Exception):
            oauth_client.exchange_code("bad-code")


class TestLoadToken:
    def test_returns_none_when_no_token(self, oauth_client):
        assert oauth_client.load_token() is None

    @patch("oauth.requests.post")
    def test_returns_token_after_exchange(self, mock_post, oauth_client):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "access123",
                "refresh_token": "refresh123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
        oauth_client.exchange_code("auth-code-123")
        token = oauth_client.load_token()
        assert token["access_token"] == "access123"


class TestRefreshToken:
    @patch("oauth.requests.post")
    def test_refreshes_with_refresh_token(self, mock_post, oauth_client):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "new-access",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
        result = oauth_client.refresh_token("refresh123")
        call_data = mock_post.call_args[1]["data"]
        assert call_data["grant_type"] == "refresh_token"
        assert call_data["refresh_token"] == "refresh123"
        assert result["access_token"] == "new-access"


class TestGetValidToken:
    @patch("oauth.requests.post")
    def test_returns_token_when_valid(self, mock_post, oauth_client):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "access123",
                "refresh_token": "refresh123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
        oauth_client.exchange_code("code")
        token = oauth_client.get_valid_token()
        assert token is not None
        assert token["access_token"] == "access123"

    def test_returns_none_when_no_token(self, oauth_client):
        assert oauth_client.get_valid_token() is None
