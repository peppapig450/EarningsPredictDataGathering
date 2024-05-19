import unittest
from unittest.mock import patch

from config.api_keys import APIKeys


class TestAPIKeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up environment variables for testing
        cls.env_vars = {
            "FMP_API_KEY": "test_fmp_api_key",
            "FINNHUB_API_KEY": "test_finnhub_api_key",
            "ALPHA_VANTAGE_API_KEY": "test_alpha_vantage_api_key",
            "APCA_KEY_ID": "test_apca_key_id",
            "APCA_API_SECRET_KEY": "test_apca_api_secret_key",
        }

    @patch("os.getenv")
    def test_from_environment_variables(self, mock_getenv):
        # Mock os.getenv to return test environment variables
        mock_getenv.side_effect = lambda key: self.env_vars.get(key)

        # Call from environment variables method
        api_keys = APIKeys.from_environment_variables()

        # Check if APIKeys object is created with the correct values
        self.assertEqual(api_keys.fmp_api_key, self.env_vars["FMP_API_KEY"])
        self.assertEqual(api_keys.finnhub_api_key, self.env_vars["FINNHUB_API_KEY"])
        self.assertEqual(
            api_keys.alpha_vantage_api_key, self.env_vars["ALPHA_VANTAGE_API_KEY"]
        )
        self.assertEqual(api_keys.apca_key_id, self.env_vars["APCA_KEY_ID"])
        self.assertEqual(
            api_keys.apca_api_secret_key, self.env_vars["APCA_API_SECRET_KEY"]
        )
