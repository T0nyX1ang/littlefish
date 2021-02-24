"""
A netcore module which negotiates with the remote server.

This module works as a kernel, and does not provide any of APIs.
The APIs are seperated into the above layers.
"""

import nonebot
import time
import traceback
import hashlib
import json
import httpx
from .config import AccountConfig
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from nonebot.log import logger

global_config = nonebot.get_driver().config
plugin_config = AccountConfig(**global_config.dict())

mswar_uid = plugin_config.mswar_uid
mswar_token = plugin_config.mswar_token
mswar_host = plugin_config.mswar_host
mswar_version = plugin_config.mswar_version
mswar_encryptor = AES.new(plugin_config.mswar_encryption_key.encode(),
                          AES.MODE_ECB)
mswar_decryptor = AES.new(plugin_config.mswar_decryption_key.encode(),
                          AES.MODE_ECB)


def _aes_encrypt(message: bytes):
    """Perform encryption on data."""
    return mswar_encryptor.encrypt(pad(message, AES.block_size)).hex().upper()


def _aes_decrypt(message: bytes):
    """Perform decryption on data."""
    return unpad(mswar_decryptor.decrypt(message), AES.block_size)


def _generate_headers(validate_hash: str):
    """Generate valid headers based on data."""
    timestamp = str(int(time.time() * 1000))
    api_key_r = mswar_uid + mswar_token + timestamp + validate_hash + 'api'
    headers = {
        'Host': mswar_host,
        'User-Agent': 'okhttp/4.7.2',
        'Accept-Encoding': 'gzip',
        'api-key': hashlib.md5(api_key_r.encode()).hexdigest(),
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'channel': 'Android',
        'device': '',
        'version': mswar_version,
        'time-stamp': timestamp,
        'token': mswar_token,
        'uid': mswar_uid,
    }
    if len(validate_hash) == 0:
        headers.pop('Content-Type')
    return headers


async def fetch(page: str = '', query: str = ''):
    """
    General module for fetching data from remote server.

    page: the page which contains the information you want to get.
    query: the query data you want to post. If "query" is empty,
           small changes will be made to fit in with the api.
    """
    try:
        hasquery = (len(query) > 0)
        data = _aes_encrypt(query.encode()) if hasquery else None
        validate_hash = hashlib.md5(data.encode()).hexdigest() if data else ''
        url = 'http://' + mswar_host + page
        async with httpx.AsyncClient() as client:  # using httpx instead
            r = await client.post(url=url,
                                  data=data,
                                  headers=_generate_headers(validate_hash))
        result = json.loads(_aes_decrypt(bytes.fromhex(r.text[32:])))
        return result  # a dictionary will be generated
    except Exception:
        logger.error(traceback.format_exc())
        return {}  # an empty dictionary will be generated
