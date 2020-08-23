import os

MAJOR = 3
MINOR = 0
PATCH = 0

BOT_NAME = 'civ-randomizer'
BOT_DESCRIPTION = 'A Discord bot for randomly selecting a subset of civs.'
BOT_EMAIL = 'civ-randomizer@mandatoryfun.xyz'
BOT_VERSION = "{}.{}.{}".format(MAJOR, MINOR, PATCH)
BOT_TOKEN = os.getenv('CIV_RANDOMIZER_TOKEN')

CONFIG_DIR = os.path.expanduser('~/.config/civ-randomizer') + os.sep
CACHE_DIR = os.path.expanduser('~/.cache/civ-randomizer') + os.sep

CONFIG_PATH = CONFIG_DIR + os.sep + 'config.json'
COMMANDS_PATH = CONFIG_DIR + os.sep + 'discord-commands.json'
PROFILE_PATH = CONFIG_DIR + os.sep + 'civ-v-profile.json'

CONFIRM_EMOJI = "\u2705"
DENY_EMOJI = "\u26d4"
