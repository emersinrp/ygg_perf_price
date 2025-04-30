import pytest
from unittest.mock import patch, MagicMock, call
import logging
import json
import time
import os
from tasks.price_task import PriceTaskSet, ALERT_THRESHOLD_SECONDS, refresher


class TestPriceTaskSet:
    @pytest.fixture
    def task_set(self):
        """Create a PriceTaskSet instance with mocked client"""
        # Create a mock parent with a mock client
        mock_parent = MagicMock()
        mock_parent.client = MagicMock()
        # Initialize TaskSet with the mock parent
        task_set = PriceTaskSet(mock_parent)
        return task_set
    
    @patch('tasks.price_task.logger')
    @patch('tasks.price_task.refresher.get_token_age')
    def test_log_result_empty(self, mock_get_token_age, mock_logger, task_set):
        """Test log_result when empty=True"""
        mock_get_token_age.return_value = 5.5
        
        task_set.log_result("Test Operation", 2.5, "BUYER123", 100, empty=True)
        
        mock_logger.warning.assert_called_once_with(
          "⚠️ EMPTY: No price data | Test Operation | buyer_code: BUYER123 | SKUs: 100 | token_age: 5.5s"
        )
    
    @patch('tasks.price_task.logger')
    @patch('tasks.price_task.refresher.get_token_age')
    def test_log_result_alert(self, mock_get_token_age, mock_logger, task_set):
        """Test log_result when elapsed > ALERT_THRESHOLD_SECONDS"""
        mock_get_token_age.return_value = 3.0
        
        task_set.log_result("Test Operation", ALERT_THRESHOLD_SECONDS + 1, "BUYER123", 100)
        
        mock_logger.warning.assert_called_once()
        assert "⚠️ ALERT" in mock_logger.warning.call_args[0][0]
    
    @patch('tasks.price_task.logger')
    @patch('tasks.price_task.refresher.get_token_age')
    def test_log_result_normal(self, mock_get_token_age, mock_logger, task_set):
        """Test log_result under normal conditions"""
        mock_get_token_age.return_value = 2.5
        
        task_set.log_result("Test Operation", 1.5, "BUYER123", 100)
        
        mock_logger.info.assert_called_once()
        assert "Test Operation reply: 1.500s" in mock_logger.info.call_args[0][0]
    
    @patch('tasks.price_task.RUN_GET_PRICE', False)
    def test_fetch_price_disabled(self, task_set):
        """Test fetch_price when RUN_GET_PRICE is False"""
        task_set.fetch_price()
        
        task_set.client.post.assert_not_called()
    
    @patch('tasks.price_task.RUN_GET_PRICE', True)
    @patch('tasks.price_task.refresher.get_token')
    def test_fetch_price_no_token(self, mock_get_token, task_set):
        """Test fetch_price when no token is available"""
        mock_get_token.return_value = None
        
        task_set.fetch_price()
        
        task_set.client.post.assert_not_called()
    
    @patch('tasks.price_task.RUN_GET_PRICE', True)
    @patch('tasks.price_task.refresher.get_token')
    @patch('tasks.price_task.settings')
    @patch('tasks.price_task.SKUS', ['SKU1', 'SKU2'])
    @patch('tasks.price_task.BUYER_CODES', ['BUYER1'])
    @patch('tasks.price_task.random.choice')
    @patch('tasks.price_task.time.time')
    def test_fetch_price_success(self, mock_time, mock_choice, mock_settings, 
                    mock_get_token, task_set):
        """Test fetch_price with successful response"""
        # Setup mocks
        mock_get_token.return_value = "fake_token"
        mock_settings.HEADERS = {"Content-Type": "application/json"}
        mock_choice.return_value = "BUYER1"
        mock_time.side_effect = [100, 102]  # start and end times
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
          "data": {
            "get_price": {
              "agregators": {"some_data": "value"}
            }
          }
        }
        task_set.client.post.return_value = mock_response
        
        # Add log_result mock to verify it's called correctly
        task_set.log_result = MagicMock()
        
        # Call method
        task_set.fetch_price()
        
        # Verify post was called with correct args
        task_set.client.post.assert_called_once()
        args = task_set.client.post.call_args[1]
        assert args["name"] == "Get price - Full SKUs"
        assert args["headers"]["Authorization"] == "Bearer fake_token"
        
        # Verify log_result was called correctly
        task_set.log_result.assert_called_once_with(
          "Get price - Full SKUs", 2, "BUYER1", 2, False
        )

    @patch('tasks.price_task.RUN_GET_PRICE', True)
    @patch('tasks.price_task.refresher.get_token')
    @patch('tasks.price_task.settings')
    @patch('tasks.price_task.SKUS', ['SKU1', 'SKU2'])
    @patch('tasks.price_task.BUYER_CODES', ['BUYER1'])
    @patch('tasks.price_task.random.choice')
    @patch('tasks.price_task.time.time')
    def test_fetch_price_empty_response(self, mock_time, mock_choice, mock_settings, 
                        mock_get_token, task_set):
        """Test fetch_price with empty response data"""
        # Setup mocks
        mock_get_token.return_value = "fake_token"
        mock_settings.HEADERS = {"Content-Type": "application/json"}
        mock_choice.return_value = "BUYER1"
        mock_time.side_effect = [100, 102]  # start and end times
        
        # Mock response with empty data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"get_price": {}}}
        task_set.client.post.return_value = mock_response
        
        # Add log_result mock to verify it's called correctly
        task_set.log_result = MagicMock()
        
        # Call method
        task_set.fetch_price()
        
        # Verify log_result was called with empty=True
        task_set.log_result.assert_called_once_with(
          "Get price - Full SKUs", 2, "BUYER1", 2, True
        )

    @patch('tasks.price_task.RUN_SKU_BLOCK', False)
    def test_fetch_price_with_random_block_disabled(self, task_set):
        """Test fetch_price_with_random_block when RUN_SKU_BLOCK is False"""
        task_set.fetch_price_with_random_block()
        
        task_set.client.post.assert_not_called()
    
    @patch('tasks.price_task.RUN_SKU_BLOCK', True)
    @patch('tasks.price_task.refresher.get_token')
    @patch('tasks.price_task.settings')
    @patch('tasks.price_task.random.choice')
    @patch('tasks.price_task.time.time')
    @patch('tasks.price_task.sku_blocks', [['SKU1', 'SKU2']])
    def test_fetch_price_with_random_block_success(self, mock_time, mock_choice, 
                             mock_settings, mock_get_token, task_set):
        """Test fetch_price_with_random_block with successful response"""
        # Setup mocks
        mock_get_token.return_value = "fake_token"
        mock_settings.HEADERS = {"Content-Type": "application/json"}
        mock_choice.side_effect = [['SKU1', 'SKU2'], "BUYER1"]  # First for sku block, then for buyer
        mock_time.side_effect = [200, 201.5]  # start and end times
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
          "data": {
            "get_price": {
              "agregators": {"some_data": "value"}
            }
          }
        }
        task_set.client.post.return_value = mock_response
        
        # Add log_result mock to verify it's called correctly
        task_set.log_result = MagicMock()
        
        # Call method
        task_set.fetch_price_with_random_block()
        
        # Verify post was called with correct args
        task_set.client.post.assert_called_once()
        args = task_set.client.post.call_args[1]
        assert args["name"] == "Get price - Block 30 SKUs"
        
        # Verify log_result was called correctly
        task_set.log_result.assert_called_once_with(
          "Get price - Block 30 SKUs", 1.5, "BUYER1", 2, False
        )