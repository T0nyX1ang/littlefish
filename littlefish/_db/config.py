"""
Configurations for the database plugin.

Please write your configurations in the global setting file.
Available configurations:
database_root: str = "database" (default)
"""

from pydantic import BaseSettings


class Config(BaseSettings):

    # Configuration goes here.
    database_location: str = "database.json"

    class Config:
        extra = "ignore"
