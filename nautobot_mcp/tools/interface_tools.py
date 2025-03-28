"""Interface and connectivity tools for Nautobot MCP.

These tools allow an LLM agent to query interface and connection data from Nautobot.
"""

from asgiref.sync import sync_to_async
from nautobot_mcp.tools.registry import register_tool
from nautobot.dcim.models.devices import Device
from nautobot.ipam.models import IPAddressToInterface


@register_tool
async def get_device_interfaces(device_name: str) -> str:
    """Get all interfaces for a specific device."""

    @sync_to_async
    def get_interfaces_sync(device_name):
        try:
            device = Device.objects.get(name=device_name)
            interfaces = device.interfaces.all()

            result = [f"Interfaces for device '{device_name}':"]

            for iface in interfaces:
                ip_assignments = IPAddressToInterface.objects.filter(interface=iface)
                ip_addresses = [str(ia.ip_address.address) for ia in ip_assignments]
                ip_str = f", IPs: {', '.join(ip_addresses)}" if ip_addresses else ""

                connected_to = ""
                if iface.cable:
                    far_end = (
                        iface.cable.termination_b
                        if iface.cable.termination_a == iface
                        else iface.cable.termination_a
                    )
                    if far_end:
                        if hasattr(far_end, "device"):
                            connected_device = far_end.device
                            far_end_name = getattr(far_end, "name", str(far_end))
                        elif hasattr(far_end, "module") and hasattr(
                            far_end.module, "device"
                        ):
                            connected_device = far_end.module.device
                            far_end_name = getattr(far_end, "name", str(far_end))
                        elif hasattr(far_end, "circuit"):
                            connected_device = None
                            circuit = far_end.circuit
                            far_end_name = (
                                f"Circuit {circuit.cid} Term {far_end.term_side}"
                            )
                        else:
                            connected_device = None
                            far_end_name = str(far_end)

                        device_name = (
                            connected_device.name
                            if connected_device
                            else "Unknown device"
                        )

                        if connected_device:
                            connected_to = (
                                f", connected to: {device_name} ({far_end_name})"
                            )
                        else:
                            connected_to = f", connected to: {far_end_name}"

                enabled = " [DISABLED]" if not iface.enabled else ""
                result.append(
                    f"- {iface.name} ({iface.type}){enabled}{ip_str}{connected_to}"
                )

            return "\n".join(result)
        except Device.DoesNotExist:
            return f"Device '{device_name}' not found."

    return await get_interfaces_sync(device_name)
