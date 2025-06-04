import inspect
import logging
import sys

from loguru import logger
from tutorialbot.core import settings


class InterceptHandler(logging.Handler):
    """A logging handler to intercept standard logging records and route them to Loguru.

    This handler converts Python's built-in logging records to Loguru log messages,
    ensuring that log levels, exception information, and caller context are preserved.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Loguru.

        Retrieves the appropriate log level for Loguru from the record, adjusts the caller
        stack depth to reflect the true source of the log message, and forwards the message
        (along with any exception details) to Loguru.

        Args
        ----
            record (logging.LogRecord): 
                The log record to be emitted.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = inspect.currentframe()
        depth = 6
        while frame is not None and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup(level: str = settings.log.level) -> None:
    """Configure Loguru and standard logging integration with OTLP support.

    This function removes any existing Loguru handlers, adds a new handler that outputs to
    stderr with the specified log level and colorization enabled, and sets up Python's built-in
    logging to use the InterceptHandler. If an OpenTelemetry endpoint is specified in the settings
    and the bot is not in DEV, it also creates an OTLPHandler to forward logs via OpenTelemetry.

    Args
    ----
        level (str, optional):
            The log level to be used. Defaults to the log level defined 
            in settings.
    """
    logger.remove()
    logger.add(sys.stderr, level=level or "DEBUG", colorize=True)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)