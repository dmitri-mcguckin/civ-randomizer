import sys, os, os.path, json, random
import civilization as civ
import utilities as utils

class CivRandomizer():
    def __init__(self, config_path=os.path.abspath(os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)) + "/config/config.json"):
        self.pool = [] # An array of Civilization objects that will be chosen from eventually
        self.blacklist = []

        #
        # Check if the config file exists first, gracefully exit if it doesn't
        #
        if(os.path.isfile(config_path)):
            self.config_path = config_path
            self.app_config = {}
        else: raise Exception(  "Config was not found in expected path: "
                                + config_path
                                + "\n\tciv-bot might not have been installed correctly!"
                                + "\n\tTry running civ-randomizer/bin/install.sh")

        #
        # Load the app config file then civ profile respectively
        #
        self.app_config = utils.load_json(self.config_path)
        self.profile = utils.load_json(self.app_config['defaults'])

        #
        # Load the blacklist
        #
        utils.log(0, "Loading the blacklist")
        self.blacklist = self.profile['blacklist']
        print("\t\tAdded " + str(len(self.blacklist)) + " civs to the blacklist!")

        #
        # Load the default civs
        #
        count = 0
        utils.log(0, "Loading base game civilizations")
        for civ_name, alt_names in self.profile['civilizations'].items():
            new_civ = civ.Civilization(civ_name, alt_names, False, not (civ_name in self.blacklist))
            self.pool.append(new_civ)
            if(utils.DEBUG): print("Adding to pool: " + str(new_civ))
            count = count + 1
        print("\t\tLoaded an additional " + str(count) + " civs!")

        #
        # Load the DLC civs
        #
        count = 0
        utils.log(0, "Loading DLC's")
        for dlc_name, dlc_data in self.profile['dlc_packs'].items():
            dlc_enabled = dlc_data['enabled']
            print("Found the DLC: " + dlc_name)

            for civ_name, alt_names in dlc_data['civs'].items():
                new_civ = civ.Civilization(civ_name, alt_names, True, (dlc_enabled and not (civ_name in self.blacklist)))
                self.pool.append(new_civ)
                if(utils.DEBUG): print("Adding to pool: " + str(new_civ))
                count = count + 1
        print("\t\tLoaded an additional " + str(count) + " civs!")

        utils.log(0, "The randomizer has been constructed!")
        print("\tTotal: " + str(len(self.pool)) + " civs | Banned: " + str(len(self.blacklist)) + " civs | Available: " + str(len(self.pool) - len(self.blacklist)) + " civs\n")

    def __del__(self):
        #
        # Save the profile back to file specified in the app config
        #
        utils.dump_json(self.app_config['defaults'], self.profile)

    def toggle_dlc(self, name, mode):
        mode_str = "disabled"
        pers_dlc_name = ""
        if(mode): mode_str = "enabled"

        for dlc_name, dlc_data in self.profile['dlc_packs'].items():
            if(dlc_name.lower().find(name) != -1):
                pers_dlc_name = dlc_name
                dlc_data['enabled'] = False

                for civ_name in dlc_data['civs'].keys():
                    for civ in self.pool:
                        if(civ_name == civ.name): civ.enabled = mode
        utils.log(0, "The DLC: " + pers_dlc_name + " has been " + mode_str + "!")
        print("\tTotal: " + str(len(self.pool)) + " civs | Banned: " + str(len(self.blacklist)) + " civs | Available: " + str(len(self.pool) - len(self.blacklist)) + " civs\n")

    def choose(self, player_count, requested_civs_per_player=None):
        players = []
        choose_pool = []
        available_max_civs = 0
        civs_per_player = 0

        #
        # Add to the temporary choose pool if enabled
        #
        for civ in self.pool:
            if(civ.enabled): choose_pool.append(civ)
        available_max_civs = len(choose_pool)
        print("There are a total of " + str(available_max_civs) + " civs to choose from this round!")

        #
        # Cross check with the blacklist that the choose pool doesn't have what it shouldn't
        #
        for banned_civ in self.blacklist:
            if(banned_civ in choose_pool): raise Exception('Whoops!\n\tThe banned civ: ' + banned_civ + ' somehow made it into the choose pool!')

        #
        # Ensures that no matter what, the choose pool will not have overflow of civs-per-player
        #
        requested_max_civs = player_count * requested_civs_per_player
        if(requested_civs_per_player == None): civs_per_player = int(available_max_civs / player_count)
        elif(requested_max_civs <= available_max_civs): civs_per_player = requested_civs_per_player
        else: civs_per_player = int(available_max_civs / player_count)

        for i in range(0, player_count):
            players.insert(i, [])

            for j in range(0, civs_per_player):
                rand = random.randint(0, available_max_civs) - 1
                players[i].append(choose_pool[rand])

                choose_pool.pop(rand)
                if(available_max_civs > 0): available_max_civs = available_max_civs - 1

        return players

def usage():
    utils.log(3, 'Invalid usage!\n\tUsage: python3 choose.py <[Int] player count> <[Int] civilization count>')

def main():
    # try:
        randomizer = CivRandomizer()
        randomizer.toggle_dlc('double civ', True)
        randomizer.toggle_dlc('kore', False)
        results = randomizer.choose(int(sys.argv[1]), int(sys.argv[2]))

        for i, list in enumerate(results):
            print("Player " + str(i + 1)+ ": [ ", end='')

            for j, civ in enumerate(list):
                print(civ.name, end='')
                if(j < len(list) - 1): print(", ", end="")
            print(" ]")

    # except Exception as e: print("\n" + str(e))

if __name__ == '__main__':
    main()
