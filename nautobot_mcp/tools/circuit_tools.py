"""Circuit tools for Nautobot MCP."""

from asgiref.sync import sync_to_async
from nautobot_mcp.tools.registry import register_tool
from nautobot.circuits.models import Circuit


@register_tool
async def get_circuit_by_id(cid: str) -> str:
    """Get circuit by CID."""

    @sync_to_async
    def get_circuit_sync(cid):
        try:
            circuit = Circuit.objects.get(cid=cid)
            report = [
                f"Circuit ID: {circuit.cid}",
                f"Provider: {circuit.provider}",
                f"Type: {circuit.circuit_type}",
                f"Status: {circuit.status}",
            ]

            if circuit.tenant:
                report.append(f"Tenant: {circuit.tenant}")
            if circuit.commit_rate:
                report.append(f"Commit Rate: {circuit.commit_rate} Kbps")
            if circuit.install_date:
                report.append(f"Install Date: {circuit.install_date}")
            if circuit.description:
                report.append(f"Description: {circuit.description}")

            return "\n".join(report)
        except Circuit.DoesNotExist:
            return f"Circuit with ID '{cid}' not found."

    return await get_circuit_sync(cid)
