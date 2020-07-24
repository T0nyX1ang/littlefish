# This file is used as a 'storage' when the program is running
# So you can regard them as variables in RAM

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import sys
import json
import getpass
import hashlib

# primary password
PRIMARY_PASSWORD = hashlib.sha3_256(getpass.getpass('Please enter your primary password: ').encode()).digest()
PRIMARY_ENCRYPT = lambda message: AES.new(PRIMARY_PASSWORD, AES.MODE_ECB).encrypt(pad(message.encode(), AES.block_size))
PRIMARY_DECRYPT = lambda message: unpad(AES.new(PRIMARY_PASSWORD, AES.MODE_ECB).decrypt(message), AES.block_size).decode()

# database paths
DATABASE_PATH = os.path.join(os.getcwd(), 'database')
GLOBAL_DATABASE_PATH = os.path.join(DATABASE_PATH, 'global')
GLOBAL_KEYS_PATH = os.path.join(GLOBAL_DATABASE_PATH, 'keys.dat')
LOCAL_DATABASE_PATH = os.path.join(DATABASE_PATH, 'local')

# database 
try:
	with open(GLOBAL_KEYS_PATH, 'rb') as f:
		GLOBAL_KEYS = json.loads(PRIMARY_DECRYPT(f.read()))
except Exception as e:
	print('Wrong password. Please retry running this program again.')
	sys.exit()

# auth module
CURRENT_ENABLED = {}

# autorepeat module
CURRENT_GROUP_MESSAGE = {}
CURRENT_COMBO_COUNTER = {}

# calc42 module
CURRENT_42_APP = {}

# info module
CURRENT_ID_COLDING_LIST = {}

# conflict module
CURRENT_CONFLICT_COUNTER = {}
