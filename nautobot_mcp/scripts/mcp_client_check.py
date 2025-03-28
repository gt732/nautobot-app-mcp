from mcp import ClientSession
from mcp.client.sse import sse_client
from rich import print


async def run():
    async with sse_client(url="http://127.0.0.1:8005/sse") as streams:
        async with ClientSession(*streams) as session:

            print("Initializing MCP session...")
            await session.initialize()

            # List available tools
            print("\nAvailable tools:")
            tools = await session.list_tools()
            for tool in tools:
                print(f"- {tool}")

            # Test get_device_interfaces tool
            print("\nTesting get_device_interfaces tool:")
            device_result = await session.call_tool(
                name="get_device_interfaces", arguments={"device_name": "ang01-edge-01"}
            )
            print(device_result.content[0].text)

            # Test get_circuit_by_id tool
            print("\nTesting get_circuit_by_id tool:")
            circuit_result = await session.call_tool(
                name="get_circuit_by_id", arguments={"cid": "ntt-104265404093023273"}
            )
            print(circuit_result.content[0].text)

            # Test get_prefix_details tool
            print("\nTesting get_prefix_details tool:")
            prefix_result = await session.call_tool(
                name="get_prefix_details", arguments={"prefix": "10.0.3.0/24"}
            )
            print(prefix_result.content[0].text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
