import sys, os, os.path, json, random
import civilization as civ
from utilities import log, load_json, Mode

class CivRandomizer():
    def __init__(self, config_path=os.path.abspath(os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)) + "/config/profile.json", verbose=False):
        self.pool = [] # An array of Civilization objects that will be chosen from eventually
        self.blacklist = [] # An array of civlization string names that will be omitted in choosing
        self.verbose = verbose # Verbose mode for the civ randomizer

        #
        # Check if the config file exists first, gracefully exit if it doesn't
        #
        if(os.path.isfile(config_path)): self.config_path = config_path
        else: raise Exception(  "Config was not found in expected path: "
                                + config_path
                                + "\n\tciv-bot might not have been installed correctly!"
                                + "\n\tTry running civ-randomizer/bin/install.sh")

        #
        # Load the app config file then civ profile respectively
        #
        self.profile = load_json(self.config_path)

        #
        # Load the blacklist
        #
        if(self.verbose): log(Mode.INFO, "Loading the blacklist")
        self.blacklist = self.profile['blacklist']
        if(self.verbose): log(Mode.DEBUG, "\t\tAdded " + str(len(self.blacklist)) + " civs to the blacklist!")

        #
        # Load the default civs
        #
        count = 0
        if(self.verbose): log(Mode.INFO, "Loading base game civilizations")
        for civ_name, alt_names in self.profile['civilizations'].items():
            new_civ = civ.Civilization(civ_name, alt_names, False, not (civ_name in self.blacklist))
            self.pool.append(new_civ)
            if(self.verbose): log(Mode.DEBUG, "\tAdding to pool: " + str(new_civ))
            count = count + 1
        if(self.verbose): log(Mode.DEBUG, "\t\tLoaded an additional " + str(count) + " civs!")

        #
        # Load the DLC civs
        #
        count = 0
        if(self.verbose): log(Mode.INFO, "Loading DLC's")
        for dlc_name, dlc_data in self.profile['dlc_packs'].items():
            dlc_enabled = dlc_data['enabled']
            if(self.verbose): log(Mode.INFO, "Found the DLC: " + dlc_name)

            for civ_name, alt_names in dlc_data['civs'].items():
                new_civ = civ.Civilization(civ_name, alt_names, True, (dlc_enabled and not (civ_name in self.blacklist)))
                self.pool.append(new_civ)
                if(self.verbose): log(Mode.INFO, "Adding to pool: " + str(new_civ))
                count = count + 1
        if(self.verbose): log(Mode.DEBUG, "\t\tLoaded an additional " + str(count) + " civs!")

        if(self.verbose):
            log(Mode.INFO, "The randomizer has been constructed!")
            log(Mode.INFO, "\tTotal: " + str(len(self.pool)) + " civs | Banned: " + str(len(self.blacklist)) + " civs | Available: " + str(len(self.pool) - len(self.blacklist)) + " civs\n")

    #
    # Disabled destructor till I figure out why system calls don't word as soon as scope is in destructor
    #
    def __del__(self): pass
        #
        # Save the profile back to file specified in the app config
        #

    def toggle_civ(self, civ_name, mode):
        mode_str = "disabled"
        pers_dlc_name = ""
        if(mode): mode_str = "enabled"

        for civ in self.pool:
            if(civ_name == civ):
                civ.enabled = mode
                civ_name = civ.name

                #
                # Dealing with the blacklist for crosscheck later
                #
                if(mode): # if the civ's being enabled
                    if(civ.name in self.blacklist): self.blacklist.remove(civ.name)
                else: # if the civ's being disabled
                    if(not civ.name in self.blacklist): self.blacklist.append(civ.name)
        if(self.verbose):
            log(Mode.INFO, "The Civ: " + civ_name + " has been " + mode_str + "!")
            log(Mode.INFO, "\tTotal: " + str(len(self.pool)) + " civs | Banned: " + str(len(self.blacklist)) + " civs | Available: " + str(len(self.pool) - len(self.blacklist)) + " civs\n")

    def toggle_dlc(self, name, mode):
        mode_str = "disabled"
        pers_dlc_name = ""
        if(mode): mode_str = "enabled"

        for dlc_name, dlc_data in self.profile['dlc_packs'].items():
            if(dlc_name.lower().find(name.lower()) != -1):
                pers_dlc_name = dlc_name
                dlc_data['enabled'] = mode
                for civ_name in dlc_data['civs'].keys():
                    self.toggle_civ(civ_name, mode)
        if(self.verbose):
            log(Mode.INFO, "The DLC: " + pers_dlc_name + " has been " + mode_str + "!")
            log(Mode.INFO, "\tTotal: " + str(len(self.pool)) + " civs | Banned: " + str(len(self.blacklist)) + " civs | Available: " + str(len(self.pool) - len(self.blacklist)) + " civs\n")

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
        if(self.verbose): log(Mode.INFO, "There are a total of " + str(available_max_civs) + " civs to choose from this round!")

        #
        # Cross check with the blacklist that the choose pool doesn't have what it shouldn't
        #
        for banned_civ in self.blacklist:
            if(banned_civ in choose_pool): raise Exception('Whoops!\n\tThe banned civ: ' + banned_civ + ' somehow made it into the choose pool!')

        #
        # Ensures that no matter what, the choose pool will not have overflow of civs-per-player
        #
        if(requested_civs_per_player == None): civs_per_player = int(available_max_civs / player_count)
        elif((player_count * requested_civs_per_player) <= available_max_civs): civs_per_player = requested_civs_per_player
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
    log(Mode.ERROR, 'Invalid usage!\n\tUsage: civ-choose <[Int] player count> <{optional} [Int] civilizations per player>')

def main():
    options = 3
    required_args = 1
    optional_args = 1
    arg_count = len(sys.argv)

    if(arg_count == 2 or arg_count == 3):
        randomizer = CivRandomizer()
        if(arg_count == 2): results = randomizer.choose(int(sys.argv[1]))
        elif(arg_count == 3): results = randomizer.choose(int(sys.argv[1]), int(sys.argv[2]))

        for i, list in enumerate(results):
            print("Player " + str(i + 1)+ ": [ ", end='')

            for j, civ in enumerate(list):
                print(civ.name, end='')
                if(j < len(list) - 1): print(", ", end="")
            print(" ]")
    else: usage()

if __name__ == '__main__':
    main()
