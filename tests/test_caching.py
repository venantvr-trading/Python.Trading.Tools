import json
import tempfile
import unittest
from pathlib import Path

from venantvr.tools.caching import dynamic_cache_to_json, dynamic_cache_to_pickle, cache_for_n_calls


# noinspection PyUnusedLocal
class TestCaching(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dynamic_cache_to_json_basic_functionality(self):
        """Test basic JSON caching functionality"""

        class MockClass:
            def __init__(self):
                self.exchange_name = "binance"

            @dynamic_cache_to_json(f"{self.temp_dir}/{{exchange_name}}/")
            def get_data(self):
                return {"price": 100, "symbol": "BTC"}

        mock_instance = MockClass()

        # First call should execute the function
        result1 = mock_instance.get_data()
        self.assertEqual(result1, {"price": 100, "symbol": "BTC"})

        # Check that cache file was created
        cache_path = Path(self.temp_dir) / "binance" / "get_data.json"
        self.assertTrue(cache_path.exists())

        # Second call should use cache
        result2 = mock_instance.get_data()
        self.assertEqual(result2, {"price": 100, "symbol": "BTC"})

        # Verify cache file content
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
            self.assertEqual(cached_data["value"], {"price": 100, "symbol": "BTC"})

    def test_dynamic_cache_to_json_custom_filename(self):
        """Test JSON caching with custom filename"""

        class MockClass:
            def __init__(self):
                self.exchange_name = "coinbase"

            @dynamic_cache_to_json(f"{self.temp_dir}/{{exchange_name}}/", cache_filename="custom_data.json")
            def get_custom_data(self):
                return {"value": "custom"}

        mock_instance = MockClass()
        result = mock_instance.get_custom_data()

        # Check custom filename was used
        cache_path = Path(self.temp_dir) / "coinbase" / "custom_data.json"
        self.assertTrue(cache_path.exists())

        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
            self.assertEqual(cached_data["value"], {"value": "custom"})

    def test_dynamic_cache_to_pickle_basic_functionality(self):
        """Test basic pickle caching functionality"""

        class MockClass:
            def __init__(self):
                self.exchange_name = "kraken"

            @dynamic_cache_to_pickle(f"{self.temp_dir}/{{exchange_name}}/")
            def get_complex_data(self):
                return {"nested": {"data": [1, 2, 3]}, "value": 42}

        mock_instance = MockClass()

        # First call should execute the function
        result1 = mock_instance.get_complex_data()
        self.assertIn("nested", result1)
        self.assertEqual(result1["value"], 42)

        # Check that cache file was created
        cache_path = Path(self.temp_dir) / "kraken" / "get_complex_data.pickle"
        self.assertTrue(cache_path.exists())

        # Second call should use cache
        result2 = mock_instance.get_complex_data()
        self.assertEqual(result2["nested"], {"data": [1, 2, 3]})

    def test_cache_for_n_calls(self):
        """Test the n-calls caching decorator"""
        call_count = 0

        @cache_for_n_calls(3)
        def get_timestamp():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        # First call
        result1 = get_timestamp()
        self.assertEqual(result1, "result_1")
        self.assertEqual(call_count, 1)

        # Second and third calls should return cached result
        result2 = get_timestamp()
        result3 = get_timestamp()
        self.assertEqual(result2, "result_1")
        self.assertEqual(result3, "result_1")
        self.assertEqual(call_count, 1)  # Function not called again

        # Fourth call should trigger new execution
        result4 = get_timestamp()
        self.assertEqual(result4, "result_2")
        self.assertEqual(call_count, 2)

        # Fifth and sixth calls should use new cached result
        result5 = get_timestamp()
        result6 = get_timestamp()
        self.assertEqual(result5, "result_2")
        self.assertEqual(result6, "result_2")
        self.assertEqual(call_count, 2)

    def test_cache_directory_creation(self):
        """Test that cache directories are created automatically"""

        class MockClass:
            def __init__(self):
                self.exchange_name = "test_exchange"
                self.market_type = "spot"

            @dynamic_cache_to_json(f"{self.temp_dir}/{{exchange_name}}/{{market_type}}/")
            def get_nested_data(self):
                return {"status": "ok"}

        mock_instance = MockClass()
        result = mock_instance.get_nested_data()

        # Check that nested directory structure was created
        expected_dir = Path(self.temp_dir) / "test_exchange" / "spot"
        self.assertTrue(expected_dir.exists())
        self.assertTrue(expected_dir.is_dir())

        cache_file = expected_dir / "get_nested_data.json"
        self.assertTrue(cache_file.exists())


if __name__ == '__main__':
    unittest.main()
