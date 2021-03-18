"""Configurations for the exclaim plugin.

Please write your configurations in the global setting file.
Available configurations:
resource_location: str = "resource.csv" (default)
resource_separator: str = "|" (default)
"""

from pydantic import BaseSettings


class ResourceConfig(BaseSettings):
    """Configurations for resource."""

    resource_location: str = "resource.csv"
    resource_separator: str = "|"
    frequent_face_id: list = [146]

    class Config:
        """Deal with extra configurations."""
        extra = "ignore"
