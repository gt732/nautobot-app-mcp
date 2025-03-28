"""Django urlpatterns declaration for nautobot_mcp app."""

from django.urls import path
from nautobot_mcp import views

app_name = "nautobot_mcp"

urlpatterns = [
    path("tools/", views.MCPToolsView.as_view(), name="mcp_tools"),
]
