import unittest
import requests
from unittest.mock import patch, MagicMock
from services.auth import get_token

class TestGetToken(unittest.TestCase):

    @patch('services.auth.requests.post')
    @patch('services.auth.settings')
    def test_get_token_success(self, mock_settings, mock_post):
        # Mock settings
        mock_settings.CLIENT_ID = "test_client_id"
        mock_settings.CLIENT_SECRET_PRD = "test_client_secret"
        mock_settings.TOKEN_URL = "https://example.com/token"

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test_access_token"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Call the function
        token = get_token()

        # Assertions
        self.assertEqual(token, "test_access_token")
        mock_post.assert_called_once_with(
            "https://example.com/token",
            data={
                "client_id": "test_client_id",
                "grant_type": "client_credentials",
                "client_secret": "test_client_secret",
                "scope": "openid"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    @patch('services.auth.requests.post')
    @patch('services.auth.settings')
    def test_get_token_failure(self, mock_settings, mock_post):
        # Mock settings
        mock_settings.CLIENT_ID = "test_client_id"
        mock_settings.CLIENT_SECRET_PRD = "test_client_secret"
        mock_settings.TOKEN_URL = "https://example.com/token"

        # Mock response with an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error")
        mock_post.return_value = mock_response

        # Call the function and assert it raises an exception
        with self.assertRaises(requests.exceptions.HTTPError):
            get_token()

        mock_post.assert_called_once_with(
            "https://example.com/token",
            data={
                "client_id": "test_client_id",
                "grant_type": "client_credentials",
                "client_secret": "test_client_secret",
                "scope": "openid"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

if __name__ == '__main__':
    unittest.main()