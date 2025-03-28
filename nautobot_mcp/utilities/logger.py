"""Logging utilities for Nautobot MCP.

This module provides a standardized way to get loggers throughout the MCP app.
"""

import logging

LOGGER_NAME = "nautobot.mcp"


def get_logger(name=None):
    """Get a logger instance.

    Args:
        name: Optional name to append to the base logger name
            (e.g. "tools" becomes "nautobot.mcp.tools")

    Returns:
        A configured logger instance
    """
    if name:
        logger_name = f"{LOGGER_NAME}.{name}"
    else:
        logger_name = LOGGER_NAME

    return logging.getLogger(logger_name)
