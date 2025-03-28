"""Location tools for Nautobot MCP.

These tools allow an LLM agent to query location-related data from Nautobot.
"""

from asgiref.sync import sync_to_async
from nautobot_mcp.tools.registry import register_tool
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models.racks import Rack


@register_tool
async def get_location_by_name(name: str) -> str:
    """Get location details by name."""

    @sync_to_async
    def get_location_sync(name):
        try:
            location = Location.objects.get(name=name)
            parent = location.parent.name if location.parent else "None"

            children = Location.objects.filter(parent=location)
            child_names = [child.name for child in children]

            racks = Rack.objects.filter(location=location)
            rack_count = racks.count()

            device_count = location.devices.count()

            return (
                f"Location: {location.name}\n"
                f"Type: {location.location_type.name}\n"
                f"Status: {location.status}\n"
                f"Parent: {parent}\n"
                f"Child Locations: {', '.join(child_names) if child_names else 'None'}\n"
                f"Rack Count: {rack_count}\n"
                f"Device Count: {device_count}\n"
                f"Description: {location.description or 'None'}"
            )
        except Location.DoesNotExist:
            return f"Location '{name}' not found."

    return await get_location_sync(name)
