import os, os.path, json
import civilization as civ
import utilities as utils
from copy import copy, deepcopy

class CivRandomizer():
    def __init__(self, config_path=os.path.abspath(os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)) + "/config/config.json"):
        self.pool = []
        self.config_exists = os.path.isfile(config_path)

        if(self.config_exists):
            self.config_path = config_path
            self.app_config = {}
        else: raise Exception( "Config was not found in expected path: "
                                                + config_path
                                                + "\n\tciv-bot might not have been installed correctly!"
                                                + "\n\tTry running civ-randomizer/bin/install.sh")

        self.app_config = utils.load_json(self.config_path)
        self.profile = utils.load_json(self.app_config['defaults'])

        utils.log(1, "Loaded main config from file: " + str(self.config_path))
        utils.log(1, "Loaded profile from file: " + str(self.app_config['defaults']))

        utils.log(1, "Loading base game civilizations:")
        for civ_name, alt_names in self.profile['base_game_civilizations'].items():
            new_civ = civ.Civilization(civ_name, alt_names)
            self.pool.append(new_civ)
            print("Adding to pool: " + str(new_civ))

        utils.log(1, "Loading DLC's:")
        for dlc_name, dlc_data in self.profile['dlc_packs'].items():
            dlc_enabled = dlc_data['enabled']
            print("Found the DLC: " + dlc_name)

            for civ_name, alt_names in dlc_data['civs'].items():
                new_civ = civ.Civilization(civ_name, alt_names, True, dlc_enabled)
                self.pool.append(new_civ)
                print("Adding to pool: " + str(new_civ))

    def __del__(self):
        utils.dump_json(self.app_config['defaults'], self.profile)

def usage():
    utils.log(3, 'Invalid usage!\n\tUsage: python3 choose.py <[Int] player count> <[Int] civilization count>')

def main():
    try:
        randomizer = CivRandomizer()
    except Exception as e:
        print("\n" + str(e))


if __name__ == '__main__':
    main()
