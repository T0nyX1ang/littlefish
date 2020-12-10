"""
Configurations for the exclaim plugin.

Please write your configurations in the global setting file.
Available configurations:
resource_location: str = "resource.csv" (default)
resource_separator: str = "|" (default)
"""

from pydantic import BaseSettings


class Config(BaseSettings):

    # Configuration goes here.
    resource_location: str = "resource.csv"
    resource_separator: str = "|"

    class Config:
        extra = "ignore"
