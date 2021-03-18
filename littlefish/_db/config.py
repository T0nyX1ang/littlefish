"""Configurations for the database plugin.

Please write your configurations in the global setting file.
Available configurations:
database_root: str = "database" (default)
"""

from pydantic import BaseSettings


class DatabaseConfig(BaseSettings):
    """Configurations for database."""

    database_location: str = "database.json.gz"
    database_compress_level: int = 9

    class Config:
        """Deal with extra configurations."""
        extra = "ignore"
