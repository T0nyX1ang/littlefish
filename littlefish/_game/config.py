"""
Configurations for the game plugin.

* Account configuration:
Please write your configurations in the global setting file.
Available configurations:
ftpts_target: list = [42, 1] (default)
ftpts_max_number: int = 13 (default)
ftpts_allowed_hours: list = [] (default)
"""

from pydantic import BaseSettings


class FTPtsConfig(BaseSettings):
    """Configurations for FTPtsGame."""

    ftpts_target: int = 42
    ftpts_max_number: int = 13
    ftpts_random_threshold: float = 0.0

    class Config:
        """Deal with extra configurations."""

        extra = "ignore"
