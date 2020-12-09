"""
Configurations for the netcore plugin.

Please write your configurations in the global setting file.
Available configurations:
mswar_uid: str = "your uid"
mswar_token: str = "your token"
mswar_host: str = "a valid address:port"
mswar_version: int = 0
mswar_encryption_key = "a valid encryption key"
mswar_decryption_key = "a valid decryption key"
"""

from pydantic import BaseSettings


class Config(BaseSettings):

    # Configuration goes here.
    mswar_uid: str = ""
    mswar_token: str = ""
    mswar_host: str = ""
    mswar_version: str = ""
    mswar_encryption_key: str = ""
    mswar_decryption_key: str = ""

    class Config:
        extra = "ignore"
