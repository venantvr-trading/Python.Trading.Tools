import logging
import os
import sys
import tempfile
import unittest
from logging.handlers import WatchedFileHandler
from unittest.mock import MagicMock

from venantvr.tools.logger import setup_logging, get_formatter, configure_stream
from venantvr.tools.stream import StreamToLogger


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary files and reset logging
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Reset logging configuration
        logging.getLogger("runtime").handlers.clear()
        logging.getLogger("runtime").setLevel(logging.WARNING)

    def test_setup_logging_basic(self):
        """Test basic logging setup"""
        logger = setup_logging(log_level=logging.DEBUG)

        self.assertEqual(logger.name, "runtime")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertTrue(len(logger.handlers) > 0)

        # Check that a StreamHandler was added
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertTrue(len(stream_handlers) > 0)

    def test_setup_logging_stdout_stderr_redirection(self):
        """Test that stdout and stderr are redirected to logger"""
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # noinspection PyUnusedLocal
            logger = setup_logging(log_level=logging.INFO)

            # Check that stdout and stderr were replaced with StreamToLogger
            self.assertIsInstance(sys.stdout, StreamToLogger)
            self.assertIsInstance(sys.stderr, StreamToLogger)

            # Check the log levels
            self.assertEqual(sys.stdout.log_level, logging.INFO)
            self.assertEqual(sys.stderr.log_level, logging.ERROR)

        finally:
            # Restore original stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def test_get_formatter(self):
        """Test get_formatter function"""
        logger = setup_logging(log_level=logging.INFO)

        # Get formatter for StreamHandler
        formatter = get_formatter(logger, logging.StreamHandler)
        self.assertIsNotNone(formatter)
        self.assertIsInstance(formatter, logging.Formatter)

        # Test with non-existent handler type
        formatter_none = get_formatter(logger, WatchedFileHandler)
        self.assertIsNone(formatter_none)

    def test_configure_stream_valid_path(self):
        """Test configure_stream with valid log file path"""
        logger = setup_logging(log_level=logging.INFO)
        log_file = os.path.join(self.temp_dir, "test.log")

        # Configure file logging
        configure_stream(logger, log_file)

        # Check that WatchedFileHandler was added
        watched_handlers = [h for h in logger.handlers if isinstance(h, WatchedFileHandler)]
        self.assertTrue(len(watched_handlers) > 0)

        # Check that log directory was created
        self.assertTrue(os.path.exists(self.temp_dir))

        # Test logging to file
        logger.info("Test message")

        # Check that log file was created and has content
        self.assertTrue(os.path.exists(log_file))

        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test message", content)

    def test_configure_stream_nested_directory(self):
        """Test configure_stream creates nested directories"""
        logger = setup_logging(log_level=logging.INFO)
        nested_path = os.path.join(self.temp_dir, "logs", "app", "test.log")

        # Configure file logging with nested path
        configure_stream(logger, nested_path)

        # Check that nested directory structure was created
        self.assertTrue(os.path.exists(os.path.dirname(nested_path)))

        # Test logging
        logger.info("Nested test message")

        # Check that log file exists and has content
        self.assertTrue(os.path.exists(nested_path))

    def test_configure_stream_empty_path_raises_error(self):
        """Test that empty log file path raises ValueError"""
        logger = setup_logging(log_level=logging.INFO)

        with self.assertRaises(ValueError) as context:
            configure_stream(logger, "")

        self.assertIn("Le chemin du fichier de log ne peut pas être vide", str(context.exception))

    def test_configure_stream_removes_duplicate_handlers(self):
        """Test that configure_stream removes duplicate WatchedFileHandler"""
        logger = setup_logging(log_level=logging.INFO)
        log_file = os.path.join(self.temp_dir, "test.log")

        # Configure file logging twice
        configure_stream(logger, log_file)
        initial_handler_count = len([h for h in logger.handlers if isinstance(h, WatchedFileHandler)])

        configure_stream(logger, log_file)
        final_handler_count = len([h for h in logger.handlers if isinstance(h, WatchedFileHandler)])

        # Should still have only one WatchedFileHandler
        self.assertEqual(initial_handler_count, 1)
        self.assertEqual(final_handler_count, 1)


class TestStreamToLogger(unittest.TestCase):

    def test_stream_to_logger_write(self):
        """Test StreamToLogger write method"""
        mock_logger = MagicMock()
        stream = StreamToLogger(mock_logger, logging.INFO)

        # Test writing a message
        stream.write("Test message\n")

        # Check that logger.log was called
        mock_logger.log.assert_called_once_with(logging.INFO, "Test message")

    def test_stream_to_logger_write_empty_message(self):
        """Test StreamToLogger ignores empty messages"""
        mock_logger = MagicMock()
        stream = StreamToLogger(mock_logger, logging.INFO)

        # Test writing empty message
        stream.write("")
        stream.write("   ")
        stream.write("\n")

        # Logger should not be called for empty messages
        mock_logger.log.assert_not_called()

    def test_stream_to_logger_flush(self):
        """Test StreamToLogger flush method"""
        mock_logger = MagicMock()
        stream = StreamToLogger(mock_logger, logging.INFO)

        # flush() should not raise an exception
        stream.flush()

    def test_stream_to_logger_recursion_prevention(self):
        """Test that StreamToLogger prevents recursion"""
        mock_logger = MagicMock()
        stream = StreamToLogger(mock_logger, logging.INFO)

        # Simulate recursion by setting in_write to True
        stream.in_write = True
        stream.write("Test message")

        # Logger should not be called when in_write is True
        mock_logger.log.assert_not_called()


if __name__ == '__main__':
    unittest.main()
