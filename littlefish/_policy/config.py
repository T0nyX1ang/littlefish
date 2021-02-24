"""
Configurations for the policy plugin.

Please write your configurations in the global setting file.
Available configurations:
policy_config_location: str = "policy.json" (default)
"""

from pydantic import BaseSettings


class Config(BaseSettings):

    # Configuration goes here.
    policy_config_location: str = "policy.json"

    class Config:
        extra = "ignore"
