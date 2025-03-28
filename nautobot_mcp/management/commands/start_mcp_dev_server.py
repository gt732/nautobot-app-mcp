from django.core.management.base import BaseCommand
import uvicorn
import os
import signal
from django.conf import settings


class Command(BaseCommand):
    help = "Start the MCP development server with auto-reload"

    def add_arguments(self, parser):
        parser.add_argument(
            "--port",
            type=int,
            default=8005,
            help="Port to run the server on",
        )

    def _get_custom_tools_dir(self):
        """Get the custom tools directory from Nautobot settings."""
        plugin_settings = settings.PLUGINS_CONFIG.get("nautobot_mcp", {})
        custom_tools_dir = plugin_settings.get("MCP_CUSTOM_TOOLS_DIR")

        if custom_tools_dir and os.path.isdir(custom_tools_dir):
            return custom_tools_dir
        elif custom_tools_dir:
            print(
                f"Warning: Configured MCP_CUSTOM_TOOLS_DIR '{custom_tools_dir}' is not a valid directory"
            )
        return None

    def _get_reload_dirs(self, custom_tools_dir):
        """Get directories to watch for auto-reload."""
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        tools_dir = os.path.join(project_root, "tools")
        reload_dirs = [tools_dir]

        if custom_tools_dir:
            reload_dirs.append(custom_tools_dir)
            print(f"Watching custom tools directory: {custom_tools_dir}")
            os.environ["NAUTOBOT_MCP_CUSTOM_TOOLS_DIR"] = custom_tools_dir
        else:
            if "NAUTOBOT_MCP_CUSTOM_TOOLS_DIR" in os.environ:
                del os.environ["NAUTOBOT_MCP_CUSTOM_TOOLS_DIR"]

        return reload_dirs

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
        custom_tools_dir = self._get_custom_tools_dir()
        reload_dirs = self._get_reload_dirs(custom_tools_dir)

        print(
            f"Starting MCP development server on http://{host}:{port} with auto-reload enabled"
        )
        print(f"Custom tools directory: {custom_tools_dir}")

        def force_reload_handler(signum, frame):
            print("Force reloading server...")
            os.kill(os.getpid(), signal.SIGTERM)

        signal.signal(signal.SIGUSR1, force_reload_handler)

        def on_reload():
            print("Changes detected - forcing server restart...")
            os.kill(os.getpid(), signal.SIGUSR1)

        uvicorn.run(
            "nautobot_mcp.management.commands.start_mcp_dev_server:create_app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=reload_dirs,
            reload_delay=0.25,
            timeout_keep_alive=0,
            timeout_graceful_shutdown=1,
        )


def create_app():
    """Create and configure the MCP application."""
    import nautobot

    nautobot.setup()

    from mcp.server.fastmcp import FastMCP
    from nautobot_mcp.tools.registry import (
        register_all_tools_with_mcp,
        discover_tools_from_directory,
    )

    mcp = FastMCP("Nautobot MCP Development Server (Auto-reload)", port=8005)
    register_all_tools_with_mcp(mcp)

    # Register custom tools if directory is specified in settings
    custom_tools_dir = os.environ.get("NAUTOBOT_MCP_CUSTOM_TOOLS_DIR")
    if custom_tools_dir:
        print(f"Registering custom tools from: {custom_tools_dir}")
        discover_tools_from_directory(mcp, custom_tools_dir)

    return mcp.sse_app()
