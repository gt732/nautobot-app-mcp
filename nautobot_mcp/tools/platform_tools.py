"""Platform tools for Nautobot MCP.

These tools allow an LLM agent to query platform-related data from Nautobot.
"""

from asgiref.sync import sync_to_async
from nautobot_mcp.tools.registry import register_tool
from nautobot.dcim.models import Platform, Device
from nautobot.virtualization.models import VirtualMachine


@register_tool
async def get_platform_by_name(name: str) -> str:
    """Get platform details by name."""

    @sync_to_async
    def get_platform_sync(name):
        try:
            platform = Platform.objects.get(name=name)

            # Get count of devices and VMs using this platform
            device_count = Device.objects.filter(platform=platform).count()
            vm_count = VirtualMachine.objects.filter(platform=platform).count()

            # Get manufacturer details
            manufacturer_info = (
                platform.manufacturer.name if platform.manufacturer else "None"
            )

            # Format network driver mappings
            driver_mappings = platform.network_driver_mappings
            driver_mapping_lines = []
            if driver_mappings:
                for library, driver in driver_mappings.items():
                    driver_mapping_lines.append(f"    - {library}: {driver}")
                driver_mapping_str = "\n".join(driver_mapping_lines)
            else:
                driver_mapping_str = "    None"

            return (
                f"Platform: {platform.name}\n"
                f"Manufacturer: {manufacturer_info}\n"
                f"Network Driver: {platform.network_driver or 'None'}\n"
                f"NAPALM Driver: {platform.napalm_driver or 'None'}\n"
                f"NAPALM Args: {platform.napalm_args or 'None'}\n"
                f"Description: {platform.description or 'None'}\n"
                f"Device Count: {device_count}\n"
                f"Virtual Machine Count: {vm_count}\n"
                f"Network Driver Mappings:\n{driver_mapping_str}\n\n"
            )
        except Platform.DoesNotExist:
            return f"Platform with name '{name}' not found."

    return await get_platform_sync(name)
