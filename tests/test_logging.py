import pytest
import logging

import charset_normalizer

logger = logging.getLogger("charset_normalizer")


class TestLogBehaviorClass:
    def test_set_stream_handler(self, caplog):
        charset_normalizer.set_logging_handler(
            "charset_normalizer", level=logging.DEBUG
        )
        logger.debug("log content should log with default format")
        for record in caplog.records:
            assert record.levelname == "DEBUG"
        assert "log content should log with default format" in caplog.text

    def test_set_stream_handler_format(self, caplog):
        charset_normalizer.set_logging_handler(
            "charset_normalizer", format_string="%(message)s"
        )
        logger.info("log content should only be this message")
        assert caplog.record_tuples == [
            (
                "charset_normalizer",
                logging.INFO,
                "log content should only be this message",
            )
        ]
