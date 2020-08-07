# Offers atomic operations to the database

import argparse
import getpass
import os
import hashlib
import json
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

parser = argparse.ArgumentParser(description='A tool to integrate with databases.')
parser.add_argument('-e', '--encrypt', action='store_true', help='Encrypt all databases.')
parser.add_argument('-d', '--decrypt', action='store_true', help='Decrypt all databases.')
parser.add_argument('-n', '--new_database', action='store_true', help='Create a new database.')
parser.add_argument('-y', '--yes', action='store_true', help='Always agree to changes.')
args = parser.parse_args()

if not args.yes:
	print('This operation is potentially harmful, please make sure you have backed up your data.')
	result = input('Still want to proceed? [Y/N] ')
	if result[0] != 'y':
		print('Operation aborted.')
		sys.exit()

# primary password
PRIMARY_PASSWORD = hashlib.sha3_256(getpass.getpass('Please enter your primary password: ').encode()).digest()
PRIMARY_ENCRYPT = lambda message: AES.new(PRIMARY_PASSWORD, AES.MODE_ECB).encrypt(pad(message.encode(), AES.block_size))
PRIMARY_DECRYPT = lambda message: unpad(AES.new(PRIMARY_PASSWORD, AES.MODE_ECB).decrypt(message), AES.block_size).decode()

# database paths
DATABASE_PATH = os.path.join(os.getcwd(), 'database')
GLOBAL_DATABASE_PATH = os.path.join(DATABASE_PATH, 'global')
GLOBAL_KEYS_PATH = os.path.join(GLOBAL_DATABASE_PATH, 'keys.dat')
LOCAL_DATABASE_PATH = os.path.join(DATABASE_PATH, 'local')

if args.new_database:
	# Create necessary directories
	print('Create relevant directories ...')
	if not os.path.isdir(DATABASE_PATH):
		os.mkdir(DATABASE_PATH)

	if not os.path.isdir(GLOBAL_DATABASE_PATH):
		os.mkdir(GLOBAL_DATABASE_PATH)

	if not os.path.isdir(LOCAL_DATABASE_PATH):
		os.mkdir(LOCAL_DATABASE_PATH)

	print('Gathering infomation ...')
	key_database = {}
	key_database['enc_key'] = input('Please enter upload key (16 bytes): ')
	key_database['dec_key'] = input('Please enter download key (16 bytes): ')
	key_database['connected_uid'] = input('Please enter connected UID: ')
	connected_password = getpass.getpass('Please enter connected password: ')
	key_database['connected_hash'] = hashlib.md5(connected_password.encode()).hexdigest()
	key_database['connected_token'] = ''

	print('Setting global keys ...')
	with open(GLOBAL_KEYS_PATH, 'wb') as f:
		f.write(PRIMARY_ENCRYPT(json.dumps(key_database)))

if args.decrypt:
	if os.path.isdir(GLOBAL_DATABASE_PATH):
		for files in os.listdir(GLOBAL_DATABASE_PATH):
			filename, fileext = os.path.splitext(files)
			if fileext == '.dat':
				print('Processing %s' % (files))

				with open(os.path.join(GLOBAL_DATABASE_PATH, files), 'rb') as f:
					data = PRIMARY_DECRYPT(f.read())

				with open(os.path.join(GLOBAL_DATABASE_PATH, filename + '.json'), 'w') as f:
					f.write(data)

	if os.path.isdir(LOCAL_DATABASE_PATH):
		for files in os.listdir(LOCAL_DATABASE_PATH):
			filename, fileext = os.path.splitext(files)
			if fileext == '.dat':
				print('Processing %s' % (files))

				with open(os.path.join(LOCAL_DATABASE_PATH, files), 'rb') as f:
					data = PRIMARY_DECRYPT(f.read())

				with open(os.path.join(LOCAL_DATABASE_PATH, filename + '.json'), 'w') as f:
					f.write(data)

if args.encrypt:
	if os.path.isdir(GLOBAL_DATABASE_PATH):
		for files in os.listdir(GLOBAL_DATABASE_PATH):
			filename, fileext = os.path.splitext(files)
			if fileext == '.json':
				print('Processing %s' % (files))

				with open(os.path.join(GLOBAL_DATABASE_PATH, files), 'r') as f:
					data = f.read()

				with open(os.path.join(GLOBAL_DATABASE_PATH, filename + '.dat'), 'wb') as f:
					f.write(PRIMARY_ENCRYPT(data))

	if os.path.isdir(LOCAL_DATABASE_PATH):
		for files in os.listdir(LOCAL_DATABASE_PATH):
			filename, fileext = os.path.splitext(files)
			if fileext == '.json':
				print('Processing %s' % (files))

				with open(os.path.join(LOCAL_DATABASE_PATH, files), 'r') as f:
					data = f.read()

				with open(os.path.join(LOCAL_DATABASE_PATH, filename + '.dat'), 'wb') as f:
					f.write(PRIMARY_ENCRYPT(data))
