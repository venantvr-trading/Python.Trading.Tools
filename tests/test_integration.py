import json
import logging
import os
import tempfile
import time
import unittest
from pathlib import Path

from python_trading_tools import (cache_for_n_calls, configure_stream,
                                   dynamic_cache_to_json, setup_logging)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary files
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Reset logging
        logging.getLogger("runtime").handlers.clear()
        logging.getLogger("runtime").setLevel(logging.WARNING)

    def test_logging_and_caching_integration(self):
        """Test that logging and caching work together"""
        # Setup logging
        logger = setup_logging(log_level=logging.INFO)
        log_file = os.path.join(self.temp_dir, "integration.log")
        configure_stream(logger, log_file)

        # Create a class that uses both logging and caching
        class TradingBot:

            def __init__(self):
                self.exchange_name = "test_exchange"
                self.logger = logging.getLogger("runtime")

            @dynamic_cache_to_json(f"{self.temp_dir}/cache/{{exchange_name}}/")
            def get_market_data(self, symbol="BTC"):
                self.logger.info(f"Fetching market data for {symbol}")
                return {"symbol": symbol, "price": 50000, "timestamp": time.time()}

            @cache_for_n_calls(2)
            def get_portfolio_balance(self):
                self.logger.info("Calculating portfolio balance")
                return {"balance": 10000, "currency": "USD"}

        bot = TradingBot()

        # Test cached method calls
        data1 = bot.get_market_data("BTC")
        data2 = bot.get_market_data("BTC")  # Should use cache

        self.assertEqual(data1, data2)

        # Test n-calls caching
        balance1 = bot.get_portfolio_balance()
        balance2 = bot.get_portfolio_balance()  # Should use cache

        self.assertEqual(balance1, balance2)

        # Verify cache file was created
        cache_file = (
            Path(self.temp_dir) / "cache" / "test_exchange" / "get_market_data.json"
        )
        self.assertTrue(cache_file.exists())

        # Verify log file has entries
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            log_content = f.read()
            self.assertIn("Fetching market data for BTC", log_content)
            self.assertIn("Calculating portfolio balance", log_content)

    def test_error_handling_with_logging(self):
        """Test error handling with logging integration"""
        logger = setup_logging(log_level=logging.ERROR)
        log_file = os.path.join(self.temp_dir, "error.log")
        configure_stream(logger, log_file)

        class ErrorProneClass:

            def __init__(self):
                self.exchange_name = "error_exchange"
                self.logger = logging.getLogger("runtime")

            @dynamic_cache_to_json(f"{self.temp_dir}/cache/{{exchange_name}}/")
            def risky_operation(self):
                self.logger.error("Something went wrong!")
                return {"status": "error", "message": "Operation failed"}

        error_instance = ErrorProneClass()
        result = error_instance.risky_operation()

        # Verify the method still works despite logging errors
        self.assertEqual(result["status"], "error")

        # Verify error was logged
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            log_content = f.read()
            self.assertIn("Something went wrong!", log_content)

    def test_multiple_cache_instances(self):
        """Test multiple instances with different cache paths"""

        class ExchangeConnector:

            def __init__(self, exchange_name):
                self.exchange_name = exchange_name
                self.api_version = "v1"

            @dynamic_cache_to_json(
                f"{self.temp_dir}/{{exchange_name}}/{{api_version}}/"
            )
            def get_exchange_info(self):
                return {
                    "name": self.exchange_name,
                    "version": self.api_version,
                    "features": ["spot", "futures"],
                }

        # Create multiple exchange connectors
        binance = ExchangeConnector("binance")
        coinbase = ExchangeConnector("coinbase")

        # Get data from both
        binance_info = binance.get_exchange_info()
        coinbase_info = coinbase.get_exchange_info()

        # Verify different data
        self.assertEqual(binance_info["name"], "binance")
        self.assertEqual(coinbase_info["name"], "coinbase")

        # Verify separate cache files were created
        binance_cache = (
            Path(self.temp_dir) / "binance" / "v1" / "get_exchange_info.json"
        )
        coinbase_cache = (
            Path(self.temp_dir) / "coinbase" / "v1" / "get_exchange_info.json"
        )

        self.assertTrue(binance_cache.exists())
        self.assertTrue(coinbase_cache.exists())

        # Verify cache contents are different
        with open(binance_cache, "r") as f:
            binance_cached = json.load(f)
        with open(coinbase_cache, "r") as f:
            coinbase_cached = json.load(f)

        self.assertEqual(binance_cached["value"]["name"], "binance")
        self.assertEqual(coinbase_cached["value"]["name"], "coinbase")


if __name__ == "__main__":
    unittest.main()
