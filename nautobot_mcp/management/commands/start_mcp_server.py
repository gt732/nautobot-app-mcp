from django.core.management.base import BaseCommand
from mcp.server.fastmcp import FastMCP
import os
from django.conf import settings
from nautobot_mcp.tools.registry import (
    register_all_tools_with_mcp,
    discover_tools_from_directory,
)
from nautobot_mcp.utilities.logger import get_logger

logger = get_logger("management.commands.start_mcp_server")


class Command(BaseCommand):
    help = "Start the MCP server in production mode"

    def add_arguments(self, parser):
        parser.add_argument(
            "--port",
            type=int,
            default=settings.PLUGINS_CONFIG.get("nautobot_mcp", {}).get(
                "MCP_PORT", 8005
            ),
            help="Port to run the server on",
        )

    def _get_custom_tools_dir(self):
        """Get the custom tools directory from Nautobot settings."""
        plugin_settings = settings.PLUGINS_CONFIG.get("nautobot_mcp", {})
        custom_tools_dir = plugin_settings.get("MCP_CUSTOM_TOOLS_DIR")

        if custom_tools_dir and os.path.isdir(custom_tools_dir):
            logger.info(f"Found valid custom tools directory: {custom_tools_dir}")
            return custom_tools_dir
        elif custom_tools_dir:
            logger.warning(
                f"Configured MCP_CUSTOM_TOOLS_DIR '{custom_tools_dir}' is not a valid directory"
            )
        return None

    def handle(self, *args, **kwargs):
        host = kwargs.get(
            "host",
            settings.PLUGINS_CONFIG.get("nautobot_mcp", {}).get(
                "MCP_HOST", "127.0.0.1"
            ),
        )
        port = kwargs.get(
            "port",
            settings.PLUGINS_CONFIG.get("nautobot_mcp", {}).get("MCP_PORT", 8005),
        )

        load_core_tools = settings.PLUGINS_CONFIG.get("nautobot_mcp", {}).get(
            "MCP_LOAD_CORE_TOOLS", False
        )

        custom_tools_dir = self._get_custom_tools_dir()

        mcp = FastMCP("Nautobot MCP Server", host=host, port=port)
        logger.info(f"Starting MCP server on http://{host}:{port}")

        if load_core_tools:
            logger.info("Registering core tools with MCP server")
            register_all_tools_with_mcp(mcp)

        if custom_tools_dir:
            logger.info(f"Registering custom tools from: {custom_tools_dir}")
            discover_tools_from_directory(mcp, custom_tools_dir)

        logger.info("MCP server initialized, starting transport")
        mcp.run(transport="sse")
