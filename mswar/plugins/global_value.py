# This file is used as a 'storage' when the program is running
# So you can regard them as variables in RAM

import os
import json

# global database loader
GLOBAL_KEYS_PATH = os.getcwd() + os.sep + 'database' + os.sep + 'global' + os.sep + 'keys.json'
with open(GLOBAL_KEYS_PATH, 'r') as f:
	GLOBAL_KEYS = json.loads(f.read())

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
