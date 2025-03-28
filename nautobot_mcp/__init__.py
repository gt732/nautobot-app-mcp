"""App declaration for nautobot_mcp."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata
from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotMcpConfig(NautobotAppConfig):
    """App configuration for the nautobot_mcp app."""

    name = "nautobot_mcp"
    verbose_name = "Nautobot Mcp"
    version = __version__
    author = "Geury Torres"
    description = "Nautobot Mcp."
    base_url = "nautobot-mcp"
    required_settings = []
    min_version = "2.0.0"
    max_version = "2.9999"
    default_settings = {
        "MCP_PORT": 8005,
        "MCP_HOST": "0.0.0.0",
        "MCP_LOAD_CORE_TOOLS": False,
    }
    caching_config = {}


config = NautobotMcpConfig
