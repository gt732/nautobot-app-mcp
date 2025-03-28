from django.db import models
from nautobot.core.models import BaseModel


class MCPTool(BaseModel):
    """Model to track MCP tools registered with the server."""

    name = models.CharField(
        max_length=255, unique=True, help_text="Name of the MCP tool function"
    )
    description = models.TextField(
        blank=True, help_text="Description of what the tool does"
    )
    module_path = models.CharField(
        max_length=255,
        help_text="Python module path where the tool is defined",
        blank=True,
    )
    parameters = models.JSONField(
        blank=True, null=True, help_text="JSON schema of the tool's parameters"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "MCP Tool"
        verbose_name_plural = "MCP Tools"

    def __str__(self):
        return self.name
