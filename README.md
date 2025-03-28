# Nautobot MCP

![Nautobot](https://img.shields.io/badge/Nautobot-2.0+-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)

This Nautobot app integrates the MCP (Model Context Protocol) server with Nautobot, providing AI-ready tools and interfaces for network automation and management.

## Overview

Nautobot MCP enables AI assistants or applications to interact with your network data through a standardized protocol. The app runs an MCP server alongside Nautobot that exposes tools which can be used by AI systems.

https://modelcontextprotocol.io/introduction

## Installation

### 1. Install the package

```bash
pip install nautobot-mcp
```

### 2. Add to INSTALLED_APPS in your Nautobot configuration

```python
# In your nautobot_config.py
PLUGINS = [
    "nautobot_mcp",
    # ... other plugins
]
```

### 3. Configuration

Configure the app through Nautobot's configuration system:

```python
# In your nautobot_config.py
PLUGINS_CONFIG = {
    "nautobot_mcp": {
        "MCP_PORT": 8005,  # MCP server port
        "MCP_HOST": "0.0.0.0",  # Default is 0.0.0.0
        "MCP_CUSTOM_TOOLS_DIR": "/path/to/your/custom/tools",  # Directory for custom tools
        "MCP_LOAD_CORE_TOOLS": False,  # Load built-in tools
    },
}
```

### 4. Run nautobot post upgrade

```bash
nautobot-server post_upgrade
```

## Custom Tools

You can create your own custom tools by defining Python functions in the directory specified in `MCP_CUSTOM_TOOLS_DIR`. 

Example custom tool:

```python
# In /path/to/your/custom/tools/my_tools.py

def some_tool(param1: str, param2: str) -> dict:
    """Some tool description"""
    # Your implementation here
    return {"result": f"Tool result for {param1} and {param2}"}
```

The MCP server will automatically discover and register all function-based tools in the specified directory.

## Deployment Options

### Method 1: Manual Start

You can start the MCP server manually:

```bash
nautobot-server start_mcp_server
```

### Method 2: Systemd Service (Recommended for Production)

Create a systemd service file at `/etc/systemd/system/nautobot-mcp.service`:

```ini
[Unit]
Description=Nautobot MCP Server
After=network-online.target
Wants=network-online.target

[Service]
User=nautobot
Group=nautobot
WorkingDirectory=/opt/nautobot
ExecStart=/opt/nautobot/venv/bin/nautobot-server start_mcp_server
Restart=on-failure
RestartSec=30
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nautobot-mcp.service
```

## Viewing Available Tools

You can view all registered tools in the Nautobot web interface at:

```
https://your-nautobot-server/plugins/nautobot-mcp/tools/
```

This page shows all available tools, their descriptions, module paths, and parameter specifications.

![Tools](static/mcp_tools_example.PNG)

## TODO

- [ ] Add a way to route tool execution to a specific Nautobot worker.
- [ ] Enhance the tool view in the Nautobot web interface to show tool usage statistics.
- [ ] Create a docker container to run the MCP server.
- [ ] Add tests.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 