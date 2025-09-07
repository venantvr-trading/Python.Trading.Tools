# Python Trading Tools

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](.)

A Python utility library designed to simplify logging and caching tasks in Python applications, particularly in trading contexts where performance and comprehensive logging are essential.

## Features

- **Dynamic Caching**: Flexible caching decorators with JSON and Pickle support
- **Advanced Logging**: Comprehensive logging setup with file and console handlers
- **Stream Redirection**: Automatic stdout/stderr redirection to logging system
- **Trading-Focused**: Optimized for financial and trading applications
- **Zero Runtime Dependencies**: No external dependencies required for core functionality

## Quick Start

### Installation

```bash
# Install from source
pip install .

# Development installation
pip install -e .

# Install with testing dependencies
pip install -e ".[dev]"
```

### Basic Usage

```python
from venantvr.tools import setup_logging, dynamic_cache_to_json
import logging

# Setup logging
logger = setup_logging(log_level=logging.INFO)

# Use caching decorator
class TradingBot:
    def __init__(self):
        self.exchange_name = "binance"
    
    @dynamic_cache_to_json("cache/{exchange_name}/")
    def get_market_data(self):
        return {"price": 50000, "symbol": "BTC/USD"}

bot = TradingBot()
data = bot.get_market_data()  # Cached automatically
```

## Requirements

- **Python**: >= 3.8
- **Development Dependencies**: pytest (optional)

## Modules Overview

### Caching Module (`caching.py`)

Provides powerful decorators for method result caching:

#### `@dynamic_cache_to_json(template_dir, cache_filename=None)`
Caches function results in JSON format with dynamic path templating.

```python
class ExchangeAPI:
    def __init__(self):
        self.exchange_name = "coinbase"
        self.api_version = "v1"
    
    @dynamic_cache_to_json("cache/{exchange_name}/{api_version}/")
    def get_trading_pairs(self):
        # This will be cached to: cache/coinbase/v1/get_trading_pairs.json
        return {"pairs": ["BTC/USD", "ETH/USD"]}
```

**Features:**
- Dynamic path templating using instance attributes
- Automatic directory creation
- Custom filename support
- JSON serialization for readable cache files

#### `@dynamic_cache_to_pickle(template_dir, cache_filename=None)`
Similar to JSON caching but uses pickle for complex Python objects.

```python
@dynamic_cache_to_pickle("cache/{exchange_name}/")
def get_complex_data(self):
    return {"data": [1, 2, 3], "func": lambda x: x * 2}
```

#### `@cache_for_n_calls(n)`
Caches results for a specific number of function calls.

```python
@cache_for_n_calls(5)
def get_live_price(self):
    # Fresh data every 5 calls
    return requests.get("https://api.exchange.com/price").json()
```

### Logging Module (`logger.py`)

Comprehensive logging setup with advanced features:

#### `setup_logging(log_level=logging.INFO)`
Configures the main application logger with console output and stdout/stderr redirection.

```python
import logging
from venantvr.tools import setup_logging

logger = setup_logging(log_level=logging.DEBUG)
logger.info("Application started")

# All print statements are automatically logged
print("This will appear in logs")
```

#### `configure_stream(runtime_logger, log_file)`
Adds file logging with automatic directory creation.

```python
from venantvr.tools import configure_stream

configure_stream(logger, "logs/trading_app.log")
logger.info("This goes to both console and file")
```

#### `get_formatter(runtime_logger, handler_type)`
Utility function to retrieve formatters from specific handler types.

### Stream Module (`stream.py`)

#### `StreamToLogger`
Internal utility class for redirecting stdout/stderr to logging system with recursion protection.

## Advanced Usage Examples

### Complete Trading Application

```python
import logging
import time
from venantvr.tools import (
    setup_logging, 
    configure_stream, 
    dynamic_cache_to_json, 
    cache_for_n_calls
)

class TradingBot:
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.logger = setup_logging(log_level=logging.INFO)
        configure_stream(self.logger, f"logs/{exchange_name}.log")
    
    @dynamic_cache_to_json("cache/{exchange_name}/market_data/")
    def get_historical_data(self, symbol, timeframe="1h"):
        self.logger.info(f"Fetching historical data for {symbol}")
        # Simulate API call
        time.sleep(1)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": [{"timestamp": time.time(), "price": 50000}]
        }
    
    @cache_for_n_calls(10)
    def get_account_balance(self):
        self.logger.info("Fetching account balance")
        return {"balance": 10000, "currency": "USD"}
    
    @dynamic_cache_to_json("cache/{exchange_name}/", cache_filename="config.json")
    def get_trading_config(self):
        return {
            "max_position_size": 1000,
            "risk_percentage": 0.02,
            "stop_loss": 0.05
        }

# Usage
bot = TradingBot("binance")
historical = bot.get_historical_data("BTC/USD", "4h")
balance = bot.get_account_balance()
config = bot.get_trading_config()
```

### Error Handling and Logging

```python
import logging
from venantvr.tools import setup_logging, configure_stream

class RobustTradingSystem:
    def __init__(self):
        self.logger = setup_logging(log_level=logging.INFO)
        configure_stream(self.logger, "logs/errors.log")
    
    def execute_trade(self, symbol, quantity):
        try:
            self.logger.info(f"Executing trade: {symbol} x {quantity}")
            # Trading logic here
            result = {"status": "success", "order_id": "12345"}
            self.logger.info(f"Trade executed successfully: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            raise
```

## Testing

The project includes comprehensive tests covering all functionality:

```bash
# Run tests with unittest
python -m unittest discover tests -v

# Run tests with pytest (if installed)
pytest

# Run tests with pytest
pytest tests/ -v
```

### Test Suite

- **Caching Tests**: All decorator functionality, file operations, directory creation
- **Logging Tests**: Logger setup, file handlers, stream redirection
- **Integration Tests**: Combined logging and caching scenarios
- **Error Handling**: Exception cases and edge conditions

## Project Structure

```
Python.Trading.Tools/
├── venantvr/
│   └── tools/
│       ├── __init__.py          # Package exports
│       ├── caching.py           # Caching decorators
│       ├── logger.py            # Logging configuration
│       └── stream.py            # Stream redirection utilities
├── tests/
│   ├── __init__.py
│   ├── test_caching.py          # Caching tests
│   ├── test_logger.py           # Logging tests
│   └── test_integration.py      # Integration tests
├── pyproject.toml               # Modern Python packaging
├── setup.py                     # Legacy setup support
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Configuration

### pytest Configuration

The project is configured for easy testing with pytest:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--verbose"
```

### Development Dependencies

Optional development dependencies can be installed with:

```bash
pip install -e ".[dev]"
```

This includes:
- `pytest>=7.0.0`: Testing framework

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

- **Author**: venantvr
- **Email**: venantvr@gmail.com
- **Repository**: [https://github.com/venantvr/Python.Trading.Tools](https://github.com/venantvr/Python.Trading.Tools)

---

*Built with ❤️ for the Python trading community*
