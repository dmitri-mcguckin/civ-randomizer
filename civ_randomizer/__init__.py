import os
import json
import logging
import civ_randomizer


def load_dict_from_json(filename: str) -> dict:
    """
    Load the given file as a python `dict`

    Parameters
    ----------
    filename: `str` an absolute path to the json file to be loaded.

    Returns
    -------
    `dict` The loaded json file as a python dictionary.
    """
    with open(filename, 'r') as file:
        return json.loads(file.read())


def save_dict_to_json(data: dict, filename: str) -> None:
    """
    Saves the given python dictionary as a json file to the given filepath

    Parameters
    ----------
    data: `dict` The python dictionary to be converted to json and written to\
           disk.
    filename: `str` An absolute path to the json file to be loaded.
    """
    with open(filename, 'w+') as file:
        file.write("{}\n".format(json.dumps(data,
                                            allow_nan=True,
                                            indent=4,
                                            check_circular=True)))


##
# Version Details
##
MAJOR = 3
MINOR = 0
PATCH = 0

##
# Bot Meta-Details
##
BOT_NAME = 'civilization-randomizer'
BOT_DESCRIPTION = 'A team-based draft-picker for Civ V with Discord integration.'
BOT_AUTHOR = 'Dmitri McGuckin'
BOT_ADMIN_ID = 198871033556631552
BOT_EMAIL = 'civ-randomizer@mandatoryfun.xyz'
BOT_URLS = {
    'home': 'https://mandatoryfun.xyz',
    'github': 'https://github.com/dmitri-mcguckin/civ-randomizer',
    'issues': 'https://github.com/dmitri-mcguckin/civ-randomizer/issues'
}
BOT_LICENSE = 'MIT'
BOT_VERSION = "{}.{}.{}".format(MAJOR, MINOR, PATCH)
BOT_TOKEN = os.getenv('CIV_RANDOMIZER_TOKEN')
BOT_LOG_LEVEL = logging.INFO
BOT_LOG_PATH = '/var/log/{}.log'.format(BOT_NAME)

OPT_DIR = os.path.abspath('/opt/{}'.format(BOT_NAME)) + os.sep
CACHE_DIR = OPT_DIR + 'cache' + os.sep
BOT_CONFIG = OPT_DIR + 'config.json'
BOT_PROFILES_DIR = CACHE_DIR + os.sep + '{}' + os.sep
BOT_CURRENT_PROFILE = BOT_PROFILES_DIR + 'current-profile.json'

ASSETS_DIR = civ_randomizer.__path__[0] + os.sep + 'assets' + os.sep
COMMANDS = load_dict_from_json(ASSETS_DIR + 'commands.json')
DEFAULT_CONFIG_ASSET = ASSETS_DIR + 'default-config.json'
DEFAULT_PROFILE_ASSET = ASSETS_DIR + 'default-civ-v-profile.json'

##
# Logging stuff
##
LOG = logging.getLogger('discord')
LOG.setLevel(BOT_LOG_LEVEL)
logging.basicConfig(level=BOT_LOG_LEVEL)
log_handler = logging.FileHandler(filename=BOT_LOG_PATH,
                                  encoding='utf-8',
                                  mode='w')
LOG.addHandler(log_handler)
