"""Gather account information for the bot."""

import os
import sys
import json


def question_prompt(question_item, default: str = ''):
    """Ask a question for the user."""
    question = 'Please enter %s (default: %s): ' % (question_item, default)
    answer = input(question)
    if not answer:
        answer = default
    print('%s has been set to: %s' % (question_item, answer))
    return answer


def prompt_when_file_exist(filename):
    """Show prompt when a file exists."""
    fullname = os.path.join(os.getcwd(), filename)
    while os.path.isfile(fullname):
        result = input('This file exists on the disk, setting current '
                       'filename will override your file! Still proceed? '
                       '[Y/n] ')

        if result and result[0].lower() == 'y':
            break

        filename = input('Please enter a new filename: ')
        fullname = os.path.join(os.getcwd(), filename)

    print('Filename has been set to: %s' % filename)
    return filename


def exit_when_file_exist(filename):
    """Stop the program when a file exists."""
    if os.path.isfile(os.path.join(os.getcwd(), filename)):
        print('This program will not proceed as a core file [%s] '
              'has been found on disk. Please check if the file already '
              'contains all the information you need. If you are sure '
              'that you will not need the file anymore, please remove '
              'it to proceed. It is strong recommended to have a backup '
              'of your file.' % filename)
        sys.exit()


def setup_default_policy():
    """Set up a default policy."""
    default_policy = {
        "dailymap": {
            "@": {
                "hour": 0,
                "minute": 3,
                "second": 0
            }
        },
        "dailystar": {
            "@": {
                "hour": 0,
                "minute": 1,
                "second": 30
            }
        },
        "autopvp": {
            "@": {
                "hour": 0,
                "minute": 0,
                "second": 0
            }
        },
        "level": {
            "@": {
                "day_of_week": 0,
                "hour": 0,
                "minute": 0,
                "second": 0
            }
        },
        "calc42": {
            "@": {
                "hour": "8-23",
                "minute": 42,
                "second": 42
            }
        },
        "group": {
            "@": {
                "hour": "3-23/4",
                "minute": 0,
                "second": 0
            }
        },
        "supercmd": {
            "+": []
        }
    }
    return default_policy


print('Hello! This is the wizard of littlefish. You need to enter some '
      'information to proceed, and the wizard will help you with basic '
      'configurations. You can see the documents if you need later on.')

print('Creating environment reference file ...')
exit_when_file_exist('.env')

config = {
    'host': '127.0.0.1',
    'port': '27182',
    'debug': 'true',
    'superusers': '',
    'command_start': '["", "/"]',
    'mswar_uid': '',
    'autopvp_uid': '',
    'mswar_token': '',
    'mswar_host': '',
    'mswar_version': '',
    'mswar_encryption_key': '',
    'mswar_decryption_key': '',
    'database_location': 'database.json.gz',
    'policy_config_location': 'policy.json',
    'resource_location': 'resource.csv',
}

print('Setting up superusers ...')
config['superusers'] = '[%s]' % question_prompt('superusers', '')

print('Setting up network ...')
for item in [
        'host', 'port', 'mswar_uid', 'autopvp_uid', 'mswar_token', 'mswar_host', 'mswar_version', 'mswar_encryption_key',
        'mswar_decryption_key'
]:
    config[item] = question_prompt(item, config[item])

print('Setting up database ...')
for item in ['database_location', 'policy_config_location', 'resource_location']:
    config[item] = prompt_when_file_exist(question_prompt(item, config[item]))

config_file = ''
for k, v in config.items():
    config_file += '%s=%s\n' % (k, v)

with open(os.path.join(os.getcwd(), '.env'), 'w') as f:
    f.write(config_file)

print('Setting up policy ...')
policy = {}
flag = True
while flag:
    try:
        args = input('Please enter a bot_id and a group_id, or enter nothing to quit: ').split()
        bid = args[0]
        gid = args[1]
        policy.setdefault(bid, {})
        policy[bid].setdefault(gid, {})
        policy[bid][gid] = setup_default_policy()
        print('Policy for [bot %s] within [group %s] completed ...' % (bid, gid))
    except Exception:
        flag = bool(args)

with open(os.path.join(os.getcwd(), config['policy_config_location']), 'w') as f:
    f.write(json.dumps(policy, indent=4, sort_keys=True, ensure_ascii=False))

print('You are all set! Run bot.py based on your to enjoy '
      'littlefish now. You can change your configurations '
      'in .env later. You can change you policy control in '
      '%s later. Happy fishing!' % (config['policy_config_location']))
