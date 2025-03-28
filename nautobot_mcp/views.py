"""Views for Nautobot MCP.

This module provides views for the Nautobot MCP app.
"""

from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import requests
from django.conf import settings
from nautobot_mcp.models import MCPTool

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_mcp", {})
HOST = PLUGIN_SETTINGS.get("MCP_HOST", "127.0.0.1")
PORT = PLUGIN_SETTINGS.get("MCP_PORT", 8005)


class MCPToolsView(LoginRequiredMixin, View):
    """View for displaying a list of all available MCP tools."""

    def check_mcp_server_status(self):
        """Check if the MCP server is running by making a connection attempt."""

        server_url = f"http://{HOST}:{PORT}/sse"

        try:
            response = requests.get(server_url, timeout=1, stream=True)

            if response.status_code == 200:
                response.close()
                return True, None
            else:
                return False, f"MCP server returned status code: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to MCP server at {HOST}:{PORT}"
        except requests.exceptions.Timeout:
            return False, f"Connection to MCP server at {HOST}:{PORT} timed out"
        except Exception as e:
            return False, f"Error checking MCP server status: {str(e)}"

    def get(self, request):
        """Handle GET requests to display MCP tools."""

        tools = MCPTool.objects.all().order_by("name")

        is_running, error_message = self.check_mcp_server_status()

        tools_list = []
        for tool in tools:
            parameters_formatted = None
            if tool.parameters:
                try:
                    parameters_formatted = json.dumps(tool.parameters, indent=2)
                except:
                    parameters_formatted = str(tool.parameters)

            tools_list.append(
                {
                    "name": tool.name,
                    "description": tool.description or "No description available",
                    "module_path": tool.module_path,
                    "parameters": parameters_formatted,
                }
            )
        mcp_status = {
            "running": is_running,
            "error": (
                None if is_running else (error_message or "MCP server is not running")
            ),
            "host": HOST,
            "port": PORT,
        }

        context = {
            "tools": tools_list,
            "mcp_status": mcp_status,
        }

        return render(request, "nautobot_mcp/tools.html", context)
