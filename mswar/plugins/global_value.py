# This file is used as a 'storage' when the program is running
# So you can regard them as variables in RAM

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode
from nonebot.log import logger
import cv2
import os
import sys
import json
import getpass
import hashlib

# document and version
DOCS_PATH = os.path.join(os.getcwd(), 'docs')
with open(os.path.join(DOCS_PATH, 'changelog.md'), 'r', encoding='utf-8') as f:
	CHANGELOG = f.read()
LATEST_CHANGELOG = CHANGELOG.split('##')[1].strip().replace('#', '')
VERSION = LATEST_CHANGELOG.splitlines()[0]
logger.info('Changelog file is loaded ...')
logger.info('Current version: %s' % VERSION)
if 'dev' in VERSION:
	logger.warning('This version is unstable, some API might be changing frequency, please handle with care !')

# resource
logger.info('Loading resource data ...')
RESOURCE_PATH = os.path.join(os.getcwd(), 'resource')
THEME_RESOURCE_PATH = os.path.join(RESOURCE_PATH, 'theme')
ADMIRE_RESOURCE_PATH = os.path.join(RESOURCE_PATH, 'admire')

THEME_RESOURCE = {}
for file in os.listdir(THEME_RESOURCE_PATH):
	filename = os.path.splitext(file)[0]
	THEME_RESOURCE[filename] = cv2.imread(os.path.join(THEME_RESOURCE_PATH, file))
	logger.info('%s loaded ...' % os.path.join(THEME_RESOURCE_PATH, file))

ADMIRE_RESOURCE = {}
for file in os.listdir(ADMIRE_RESOURCE_PATH):
	filename = os.path.splitext(file)[0]
	with open(os.path.join(ADMIRE_RESOURCE_PATH, file), 'rb') as f:
		fin = f.read()
		ADMIRE_RESOURCE[filename] = b64encode(fin).decode()
	logger.info('%s loaded ...' % os.path.join(ADMIRE_RESOURCE_PATH, file))

# message policy
POLICY_PATH = os.path.join(os.getcwd(), 'policy.json')
if os.path.isfile(POLICY_PATH):
	try:
		with open(POLICY_PATH, 'r') as f:
			POLICY = json.loads(f.read())
			logger.info('Policy file is loaded ...')
	except Exception as e:
		logger.error('Failed to load the policy file, please try again ...')
		sys.exit()
else:
	logger.info('No policy file is found, using PASS policy in all groups ...')
	POLICY = {}

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
	logger.error('Wrong password. Please retry running this program again.')
	sys.exit()

logger.info('Initializing global values ...')

# global switch
CURRENT_ENABLED = {}

# autorepeat module
CURRENT_GROUP_MESSAGE = {}
CURRENT_GROUP_MESSAGE_INCREMENT = {}
CURRENT_COMBO_COUNTER = {}

# calc42 module
CURRENT_42_APP = {}
CURRENT_42_PROB_LIST = {}

# info module
CURRENT_ID_COLDING_LIST = {}

# conflict module
CURRENT_CONFLICT_COUNTER = {}

# group members
CURRENT_GROUP_MEMBERS = {}

# repeatition word blacklist
CURRENT_WORD_BLACKLIST = {}

# global game frequency
GAME_FREQUENCY = {}
