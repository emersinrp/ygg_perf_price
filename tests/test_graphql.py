import unittest
from unittest.mock import patch, MagicMock
import requests
from services.graphql import get_price

class TestGetPrice(unittest.TestCase):

    @patch("services.graphql.requests.post")
    @patch("services.graphql.settings")
    def test_get_price_success(self, mock_settings, mock_post):
        # Mock settings
        mock_settings.HEADERS = {"Content-Type": "application/json"}
        mock_settings.PRICE_URL = "http://mockurl.com"

        # Mock token
        token = "mock_token"

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"get_price": "mocked_data"}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Call the function
        result = get_price(token)

        # Assertions
        self.assertEqual(result, {"data": {"get_price": "mocked_data"}})
        mock_post.assert_called_once_with(
            "http://mockurl.com",
            json={
                "query": "query MyQuery { get_price(filters: {sku_code: [\"000000000000031933\"], rounded: 2, payment_code: \"R019\", condition: \"YB2B\", distribution_channel_code: \"10\", buyer_code: \"0007554445\", fifo_range: [\"Z100\", \"Z098\", \"Z101\", \"Z102\"]}) { agregators { sales_region_agregator { sales_organization_agregator { price_sales_agregator { edges { node { distribution_channel_code material_type_size_agregator { box { brl { price_itens { sku_code item_category_agregator { item_category_code price_detail { base_price price discount_price tributary_substitution_price tributary_substitution_discount_price discount_percent } } } } } } } } } } } } } }"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer mock_token"
            }
        )

    @patch("services.graphql.requests.post")
    @patch("services.graphql.settings")
    def test_get_price_failure(self, mock_settings, mock_post):
        # Mock settings
        mock_settings.HEADERS = {"Content-Type": "application/json"}
        mock_settings.PRICE_URL = "http://mockurl.com"

        # Mock token
        token = "mock_token"

        # Mock response to raise an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Mock HTTP Error")
        mock_post.return_value = mock_response

        # Call the function and assert it raises an exception
        with self.assertRaises(requests.exceptions.HTTPError):
            get_price(token)

        mock_post.assert_called_once_with(
            "http://mockurl.com",
            json={
                "query": "query MyQuery { get_price(filters: {sku_code: [\"000000000000031933\"], rounded: 2, payment_code: \"R019\", condition: \"YB2B\", distribution_channel_code: \"10\", buyer_code: \"0007554445\", fifo_range: [\"Z100\", \"Z098\", \"Z101\", \"Z102\"]}) { agregators { sales_region_agregator { sales_organization_agregator { price_sales_agregator { edges { node { distribution_channel_code material_type_size_agregator { box { brl { price_itens { sku_code item_category_agregator { item_category_code price_detail { base_price price discount_price tributary_substitution_price tributary_substitution_discount_price discount_percent } } } } } } } } } } } } } }"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer mock_token"
            }
        )

if __name__ == "__main__":
    unittest.main()