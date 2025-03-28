"""Tool registry for Nautobot MCP.

This module provides the registry for MCP tools and the functionality
to register and manage them.
"""

from typing import Dict, Callable, Any
import inspect
import pkgutil
import importlib
import sys
from pathlib import Path
from functools import wraps
from django.db import transaction

from nautobot_mcp.utilities.logger import get_logger
from nautobot_mcp.models import MCPTool

logger = get_logger("tools.registry")

# Dict to store all registered tools
_tool_registry: Dict[str, Callable] = {}


def register_tool(func: Callable) -> Callable:
    """Decorator to register a function as an MCP tool.

    This doesn't attach it to an MCP server instance directly, but rather
    registers it in the global registry for later use and persists it to the database.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    _tool_registry[func.__name__] = func

    module_path = func.__module__

    description = func.__doc__ or ""

    try:
        sig = inspect.signature(func)
        parameters = {}
        for name, param in sig.parameters.items():
            param_info = {
                "name": name,
                "required": param.default == inspect.Parameter.empty,
            }

            if param.annotation != inspect.Parameter.empty:
                if hasattr(param.annotation, "__name__"):
                    param_info["type"] = param.annotation.__name__

            if param.default != inspect.Parameter.empty:
                param_info["default"] = str(param.default)

            parameters[name] = param_info
    except Exception as e:
        logger.warning(f"Error extracting parameters for {func.__name__}: {e}")
        parameters = {}

    try:
        with transaction.atomic():
            tool, created = MCPTool.objects.get_or_create(
                name=func.__name__,
                defaults={
                    "description": description,
                    "module_path": module_path,
                    "parameters": parameters,
                },
            )

            if not created:
                tool.description = description
                tool.module_path = module_path
                tool.parameters = parameters
                tool.save()

                logger.info(f"Updated existing tool in database: {func.__name__}")
            else:
                logger.info(f"Registered new tool in database: {func.__name__}")
    except Exception as e:
        logger.error(f"Failed to register tool {func.__name__} in database: {e}")

    return wrapper


def get_all_tools() -> Dict[str, Callable]:
    """Return all registered tools."""
    return _tool_registry.copy()


def discover_tools() -> None:
    """Automatically discover and import tool modules in the tools directory.

    This will look for any Python modules in the tools directory and import them,
    which will trigger registration of any tools decorated with @register_tool.
    """
    tools_dir = Path(__file__).parent

    for _, module_name, is_pkg in pkgutil.iter_modules([str(tools_dir)]):
        if module_name != "registry" and not is_pkg:
            importlib.import_module(f"nautobot_mcp.tools.{module_name}")


def discover_tools_from_directory(mcp_instance: Any, tools_dir: str) -> None:
    """Discover and register tools from a custom directory.

    Args:
        mcp_instance: An instance of the MCP server class
        tools_dir: Path to directory containing Python modules with tools
    """
    tools_path = Path(tools_dir)

    if not tools_path.exists() or not tools_path.is_dir():
        logger.warning(
            f"Custom tools directory {tools_dir} does not exist or is not a directory"
        )
        return

    parent_dir = str(tools_path.parent)
    tools_dir_name = tools_path.name

    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    discovered_custom_tools = set()

    try:
        for _, module_name, is_pkg in pkgutil.iter_modules([str(tools_path)]):
            if not is_pkg:
                try:
                    module = importlib.import_module(f"{tools_dir_name}.{module_name}")

                    for name, obj in inspect.getmembers(module, inspect.isfunction):
                        discovered_custom_tools.add(name)
                        decorated_tool = register_tool(obj)
                        mcp_instance.tool()(decorated_tool)
                        logger.info(f"Registered custom tool: {name}")
                except Exception as e:
                    logger.error(f"Error loading custom tool module {module_name}: {e}")
        try:
            with transaction.atomic():
                custom_tools_query = MCPTool.objects.filter(
                    module_path__startswith=f"{tools_dir_name}."
                )
                removed_tools = custom_tools_query.exclude(
                    name__in=discovered_custom_tools
                )

                if removed_tools.exists():
                    removed_count = removed_tools.delete()[0]
                    logger.info(
                        f"Deleted {removed_count} custom tools that no longer exist"
                    )
        except Exception as e:
            logger.error(f"Failed to delete obsolete custom tools: {e}")

    finally:
        if parent_dir in sys.path:
            sys.path.remove(parent_dir)


def register_all_tools_with_mcp(mcp_instance: Any) -> None:
    """Register all tools with the given MCP server instance.

    Args:
        mcp_instance: An instance of the MCP server class
    """
    discover_tools()

    for tool_name, tool_func in _tool_registry.items():
        mcp_instance.tool()(tool_func)
        logger.info(f"Registered core tool: {tool_name}")

    try:
        active_tool_names = set(_tool_registry.keys())
        MCPTool.objects.exclude(name__in=active_tool_names).delete()
        logger.info(f"Deleted tools not in registry")
    except Exception as e:
        logger.error(f"Failed to delete obsolete tools: {e}")
