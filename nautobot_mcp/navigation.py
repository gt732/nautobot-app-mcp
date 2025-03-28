from nautobot.core.apps import NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        name="MCP Tools",
        link="plugins:nautobot_mcp:mcp_tools",
        permissions=["nautobot_mcp.view_mcp_tool"],
    ),
)

menu_items = (
    NavMenuTab(
        name="Nautobot MCP",
        groups=(NavMenuGroup(name="Main", items=items),),
    ),
)
