"""Device tools for Nautobot MCP."""

from asgiref.sync import sync_to_async
from nautobot_mcp.tools.registry import register_tool
from nautobot.dcim.models import Device
from nautobot.circuits.models import CircuitTermination


@register_tool
async def get_device_details(device_name: str) -> str:
    """Get device details by name."""

    @sync_to_async
    def get_device_details_sync(device_name):
        try:
            device = Device.objects.get(name=device_name)

            primary_ip4_info = f"{device.primary_ip4}" if device.primary_ip4 else "None"
            primary_ip6_info = f"{device.primary_ip6}" if device.primary_ip6 else "None"
            primary_ip_info = (
                f"{device.primary_ip}"
                if hasattr(device, "primary_ip") and device.primary_ip
                else "None"
            )

            location_info = device.location.name if device.location else "None"
            rack_info = (
                f"{device.rack.name} (Position: {device.position})"
                if device.rack
                else "None"
            )

            interface_count = device.all_interfaces.count()
            console_port_count = device.all_console_ports.count()
            console_server_port_count = device.all_console_server_ports.count()
            power_port_count = device.all_power_ports.count()
            power_outlet_count = device.all_power_outlets.count()
            front_port_count = device.all_front_ports.count()
            rear_port_count = device.all_rear_ports.count()

            child_devices = device.get_children()
            child_device_count = child_devices.count()
            child_device_names = (
                ", ".join([child.name for child in child_devices[:5]])
                if child_devices
                else "None"
            )
            if child_devices.count() > 5:
                child_device_names += f" and {child_devices.count() - 5} more"

            vc_master = device.get_vc_master()
            vc_master_info = vc_master.name if vc_master else "None"

            cable_count = len(device.get_cables(pk_list=True))

            device_info = (
                f"Name: {device.name}\n"
                f"Type: {device.device_type}\n"
                f"Status: {device.status}\n"
                f"Role: {device.role.name if device.role else 'None'}\n"
                f"Platform: {device.platform.name if device.platform else 'None'}\n"
                f"Tenant: {device.tenant.name if device.tenant else 'None'}\n"
                f"Serial: {device.serial or 'None'}\n"
                f"Asset Tag: {device.asset_tag or 'None'}\n"
                f"Location: {location_info}\n"
                f"Rack: {rack_info}\n"
                f"Primary IP: {primary_ip_info}\n"
                f"Primary IPv4: {primary_ip4_info}\n"
                f"Primary IPv6: {primary_ip6_info}\n"
                f"Virtual Chassis: {device.virtual_chassis.name if device.virtual_chassis else 'None'}\n"
                f"VC Position: {device.vc_position or 'None'}\n"
                f"VC Priority: {device.vc_priority or 'None'}\n"
                f"VC Master: {vc_master_info}\n"
                f"Cluster: {device.cluster.name if device.cluster else 'None'}\n"
                f"Software Version: {device.software_version or 'None'}\n"
                f"Created: {device.created}\n"
                f"Last Updated: {device.last_updated}\n"
                f"Comments: {device.comments or 'None'}"
            )

            interfaces = device.all_interfaces.all()
            interface_details = []
            if interfaces:
                for iface in interfaces:
                    ip_assignments = (
                        iface.ip_addresses.all()
                        if hasattr(iface, "ip_addresses")
                        else []
                    )
                    ip_addresses = [str(ip.address) for ip in ip_assignments]

                    connected_to = ""
                    if hasattr(iface, "cable") and iface.cable:
                        far_end = (
                            iface.cable.termination_b
                            if iface.cable.termination_a == iface
                            else iface.cable.termination_a
                        )
                        if far_end:
                            if hasattr(far_end, "device"):
                                connected_device = far_end.device
                            elif hasattr(far_end, "module") and hasattr(
                                far_end.module, "device"
                            ):
                                connected_device = far_end.module.device
                            else:
                                connected_device = None

                            device_name = (
                                connected_device.name
                                if connected_device
                                else "Unknown device"
                            )

                            far_end_identifier = ""
                            if isinstance(far_end, CircuitTermination):
                                far_end_identifier = f"Circuit {far_end.circuit.cid} (Term {far_end.term_side})"
                            elif hasattr(far_end, "name"):
                                far_end_identifier = far_end.name
                            else:
                                far_end_identifier = str(far_end)

                            connected_to = (
                                f", connected to: {device_name} ({far_end_identifier})"
                            )

                    module_info = (
                        f" [Module: {iface.module.name}]"
                        if hasattr(iface, "module") and iface.module
                        else ""
                    )

                    lag_info = f" (LAG member: {iface.lag.name})" if iface.lag else ""

                    vlan_info = ""
                    if hasattr(iface, "untagged_vlan") and iface.untagged_vlan:
                        vlan_info += f", Untagged VLAN: {iface.untagged_vlan}"

                    if hasattr(iface, "tagged_vlans") and iface.tagged_vlans.exists():
                        tagged_vlans = iface.tagged_vlans.all()[:5]
                        if tagged_vlans:
                            vlan_list = ", ".join([str(vlan) for vlan in tagged_vlans])
                            vlan_info += f", Tagged VLANs: {vlan_list}"
                            if iface.tagged_vlans.count() > 5:
                                vlan_info += (
                                    f" (+{iface.tagged_vlans.count() - 5} more)"
                                )

                    interface_details.append(
                        f"  - {iface.name}{module_info}{lag_info}: {iface.type}, "
                        f"MTU: {iface.mtu or 'Auto'}, "
                        f"MAC: {iface.mac_address or 'N/A'}, "
                        f"Status: {'Enabled' if getattr(iface, 'enabled', True) else 'Disabled'}, "
                        f"IPs: {', '.join(ip_addresses) or 'None'}"
                        f"{vlan_info}"
                        f"{connected_to}"
                    )

                interface_summary = "\n".join(interface_details)
            else:
                interface_summary = "  No interfaces found"

            component_summary = (
                f"\nComponent Summary:\n"
                f"  Interfaces: {interface_count}\n"
                f"  Console Ports: {console_port_count}\n"
                f"  Console Server Ports: {console_server_port_count}\n"
                f"  Power Ports: {power_port_count}\n"
                f"  Power Outlets: {power_outlet_count}\n"
                f"  Front Ports: {front_port_count}\n"
                f"  Rear Ports: {rear_port_count}\n"
                f"  Connected Cables: {cable_count}\n"
                f"  Child Devices: {child_device_count} ({child_device_names})"
            )

            interface_detail_section = f"\nInterface Details:\n{interface_summary}"

            return device_info + component_summary + interface_detail_section

        except Device.DoesNotExist:
            return f"Device with name '{device_name}' not found."

    return await get_device_details_sync(device_name)
