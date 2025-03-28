"""IPAM tools for Nautobot MCP.

These tools allow an LLM agent to query IP Address Management data from Nautobot.
"""

from asgiref.sync import sync_to_async
from nautobot_mcp.tools.registry import register_tool
from nautobot.ipam.models import IPAddress, Prefix


@register_tool
async def get_ip_by_host(host: str) -> str:
    """Get IP address details by its host (e.g., '192.168.1.1')."""

    @sync_to_async
    def get_ip_sync(host):
        try:
            ip = IPAddress.objects.get(host=host)
            interfaces_info = (
                ", ".join(str(i.interface) for i in ip.interface_assignments.all())
                if ip.interface_assignments.all()
                else "None"
            )
            vm_interfaces_info = (
                ", ".join(
                    str(vmi.vm_interface) for vmi in ip.vm_interface_assignments.all()
                )
                if hasattr(ip, "vm_interface_assignments")
                and ip.vm_interface_assignments.all()
                else "None"
            )
            tenant_info = ip.tenant.name if ip.tenant else "None"
            nat_inside_info = str(ip.nat_inside) if ip.nat_inside else "None"
            nat_outside_list = (
                ", ".join(str(nat) for nat in ip.nat_outside.all())
                if hasattr(ip, "nat_outside") and ip.nat_outside.all()
                else "None"
            )
            parent_info = str(ip.parent) if ip.parent else "None"

            return (
                f"IP: {ip.address}\n"
                f"Host: {ip.host}\n"
                f"Mask Length: {ip.mask_length}\n"
                f"Type: {ip.type}\n"
                f"IP Version: {ip.ip_version}\n"
                f"DNS Name: {ip.dns_name or 'None'}\n"
                f"Status: {ip.status}\n"
                f"Role: {ip.role or 'None'}\n"
                f"Description: {ip.description or 'None'}\n"
                f"Parent Prefix: {parent_info}\n"
                f"Tenant: {tenant_info}\n"
                f"NAT Inside: {nat_inside_info}\n"
                f"NAT Outside IPs: {nat_outside_list}\n"
                f"Assigned Device Interfaces: {interfaces_info}\n"
                f"Assigned VM Interfaces: {vm_interfaces_info}\n"
                f"Created: {ip.created}\n"
                f"Last Updated: {ip.last_updated}\n"
                f"Tags: {', '.join(str(tag) for tag in ip.tags.all()) or 'None'}"
            )
        except IPAddress.DoesNotExist:
            return f"IP address '{host}' not found."

    return await get_ip_sync(host)


@register_tool
async def get_prefix_details(prefix: str) -> str:
    """Get prefix details by prefix (e.g., '10.0.0.0/24')."""

    @sync_to_async
    def get_prefix_sync(prefix):
        try:
            prefix = Prefix.objects.get(prefix=prefix)
            if prefix.locations:
                prefix_locations = ", ".join(
                    str(location) for location in prefix.locations.all()
                )
            else:
                prefix_locations = "None"
            return (
                f"Prefix: {prefix.prefix}\n"
                f"Type: {prefix.type}\n"
                f"Status: {prefix.status}\n"
                f"Role: {prefix.role or 'None'}\n"
                f"VLAN: {prefix.vlan.name if prefix.vlan else 'None'}\n"
                f"Description: {prefix.description or 'None'}\n"
                f"Tenant: {prefix.tenant.name if prefix.tenant else 'None'}\n"
                f"Location: {prefix_locations}\n"
                f"Tags: {', '.join(str(tag) for tag in prefix.tags.all()) or 'None'}"
            )
        except Prefix.DoesNotExist:
            return f"Prefix '{prefix}' not found."

    return await get_prefix_sync(prefix)
