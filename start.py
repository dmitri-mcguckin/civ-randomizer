#!/usr/bin/env python3
import os, sys
from ftf_utilities import log, Mode, load_json, dump_json
from civ_randomizer.civ_bot import CivBot

def load_token(path):
    if(not os.path.exists(path)):
        dump_json(token_dir, {'token': ''})
        log(Mode.ERROR, "Missing token in config: " + path \
                        + '\n\tPlease add a Discord Bot Token to this file before relaunching the bot.' \
                        + '\n\t(You can generate a token from here: https://discordapp.com/developers/applications)')
        sys.exit(-1)

    token = load_json(path)['token']

    if(token == None or token == ''):
        log(Mode.ERROR, "Missing token in config: " + path \
                        + '\n\tPlease add a Discord Bot Token to this file before relaunching the bot.' \
                        + '\n\t(You can generate a token from here: https://discordapp.com/developers/applications)')
        sys.exit(-1)
    return token

config = load_json('res/meta.json')
commands = load_json('res/commands.json')
default_profile = load_json('res/default_profile.json')
conf_dir = os.path.expanduser(config['cache_dir'])
token_dir = conf_dir + os.sep + 'token.json'
cache_dir = conf_dir + os.sep + 'guilds'

if(not os.path.exists(cache_dir)):
    # Generate the cache directory
    log(Mode.WARN, 'Cache dir notc found: ' + str(cache_dir) + '\n\tAutomatically generating...')
    os.makedirs(conf_dir)
    os.makedirs(cache_dir)

# Load the token cfg and subsequent token.
token = load_token(token_dir)

conf = [conf_dir, cache_dir]
bot = CivBot(token, commands, default_profile, conf, verbose = False)
bot.run()
