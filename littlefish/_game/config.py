"""
Configurations for the game plugin.

* Account configuration:
Please write your configurations in the global setting file.
Available configurations:
ftpts_target: int = 42 (default)
ftpts_max_number: int = 13 (default)
ftpts_allowed_hours: list = [] (default)
"""

from pydantic import BaseSettings


class FTPtsConfig(BaseSettings):

    # Configuration goes here.
    ftpts_target: int = 42
    ftpts_max_number: int = 13
    ftpts_allowed_hours: list = []

    class Config:
        extra = "ignore"
