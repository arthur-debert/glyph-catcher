import logging
import os


def setup_logging(debug: bool = False) -> logging.Logger:
    """Setup logging configuration.

    Args:
        debug: If True, sets logging level to DEBUG and writes to /tmp/unifill.log
              If False, sets logging level to WARN

    Returns:
        The configured logger instance
    """
    logger = logging.getLogger("uniff")

    if debug:
        logger.setLevel(logging.DEBUG)
        # Ensure the /tmp directory exists
        os.makedirs("/tmp", exist_ok=True)

        # Setup file handler
        file_handler = logging.FileHandler("/tmp/unifill.log")
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(file_handler)

        # Emit debug detected message
        logger.debug("debug detected")
    else:
        logger.setLevel(logging.WARN)
        # Add a null handler to avoid "No handlers could be found" warning
        logger.addHandler(logging.NullHandler())

    return logger
