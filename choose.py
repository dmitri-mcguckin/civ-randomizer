import random, sys, math, json, copy
import utilities as utils
from copy import copy, deepcopy

class CivRandomizer():
    def __init__(self, config_path='defaults.json'):
        self.config_path= config_path
        config_file = open(self.config_path, mode='r')
        data = config_file.read()
        config_file.close()
        self.config = json.loads(data)

        self.reform_pool()

    def __del__(self):
        if(utils.DEBUG): utils.log(2, 'Destructing pool and writing config back to file!')
        data = json.dumps(self.config, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=2, separators=None, default=None, sort_keys=True)

        if(self.config_path == 'defaults.json'):
            self.config_path = './profile_1.json'
            utils.log(1, 'The profile was set to default, creating a new profile and writing to: ' + self.config_path)


        config_file = open(self.config_path, mode='w')
        config_file.write(data)
        config_file.close()

    def reform_pool(self):
        self.choose_pool = deepcopy(self.config['default_civilization_pool'])

        for k,v in self.config['dlc_packs'].items():
            if(v[0]):
                self.choose_pool.append(v[1])
            else:
                utils.log(1, 'The ' + str(k) + ' dlc has been disabled!')

        for i in self.config['blacklist']:
            utils.log(1, 'The civilization: ' + str(i) + ' has been blacklisted and will not be considered in the pool choosing!')
            if i in self.choose_pool:
                self.choose_pool.remove(i)
        self.choose_pool = utils.flatten_list(self.choose_pool)
        self.choose_pool.sort()
        self.pool_size = len(self.choose_pool)

    def update_pool_size(self):
        self.pool_size = len(self.choose_pool)
        return self.pool_size

    def get_choose_pool(self):
        return self.choose_pool

    def get_blacklist(self):
        return self.config['blacklist']

    def add_to_blacklist(self, civilization):
        civilization = civilization[0].upper() + civilization[1:len(civilization)].lower()

        if(civilization not in self.config['blacklist']):
            self.config['blacklist'].append(civilization)
            self.reform_pool()

        if(utils.DEBUG): utils.log(0, 'Added ' + civilization + ' to the blacklist!')

    def remove_from_blacklist(self, civilization):
        civilization = civilization[0].upper() + civilization[1:len(civilization)].lower()

        if(civilization in self.config['blacklist']):
            self.config['blacklist'].remove(civilization)
            self.reform_pool()

        if(utils.DEBUG): utils.log(0, 'Removed ' + civilization + ' from the blacklist!')

    def empty_blacklist(self):
        self.config['blacklist'] = []

    def get_dlcs(self):
        results = {}

        for k,v in self.config['dlc_packs'].items():
            results[k] = { 'enabled': v[0] }
        return results

    def toggle_all_dlcs(self, mode):
        for k,v in self.config['dlc_packs'].items():
            v[0] = mode

    def toggle_dlc(self, dlc, mode):
        dlc = dlc.lower()

        for k,v in self.config['dlc_packs'].items():
            if(dlc in k.lower()):
                utils.log(1, 'Matched: "' + k + '" from "' + dlc + '"!')
                v[0] = mode
                return True
        return False

    def recommended_pool_size(self, player_count, civilization_count):
        return math.floor(civilization_count / player_count)

    def choose(self, player_count, civilization_count=None):
        if(civilization_count == None):
            civilization_count = self.recommended_pool_size(player_count, self.pool_size)
            if(utils.DEBUG): utils.log(2, 'Using recommended shared pool size: ' + str(civilization_count))
        elif(player_count * civilization_count > self.pool_size):
            utils.log(3, 'Cannot perform choose operation!\n\tThere are only ' + str(self.pool_size) + ' civilizations in the pool and there would need to be ' + str(player_count * civilization_count) + ' civilizations to complete ' + str(player_count) + ' sets of size ' + str(civilization_count))
            return {}

        session_pool = self.choose_pool.copy()
        session_size = self.pool_size
        results = {}

        if(utils.DEBUG): utils.log(2, 'Starting new choose session with the following pool: [size: ' + str(session_size) + ']\n\t' + str(session_pool))

        # Selection for individual player
        for player in range(1, player_count  + 1):
            player_name = 'Player' + str(player)
            results[player_name] = []

            # Selection of random civs
            for i in range(0, civilization_count):
                position = random.randint(0, session_size - 1)
                new_civ = session_pool.pop(position)
                results[player_name].append(new_civ)
                session_size -= 1
        return results

def usage():
    utils.log(3, 'Invalid usage!\n\tUsage: python3 choose.py <[Int] player count> <[Int] civilization count>')

def main():
    argc = len(sys.argv) - 1
    if(utils.DEBUG): utils.log(2, 'ARGS: ' + str(sys.argv) + '\tARG COUNT: ' + str(argc))

    if(argc == 1 or argc == 2):
        randomizer = CivRandomizer()
        if(utils.DEBUG):
            utils.log(2, '\tDLCS:\t' + str(randomizer.get_dlcs())
                       + '\n\t\tBlacklist:\t' + str(randomizer.get_blacklist())
                       + '\n\t\tChoose Pool:\t' + str(randomizer.choose_pool))

        randomizer.toggle_all_dlcs(True)

        if(argc == 1):
            results = randomizer.choose(int(sys.argv[1]))
            for i in results:
                utils.log(0, i + ': ' + str(results[i]))
        else:
            results = randomizer.choose(int(sys.argv[1]), civilization_count=int(sys.argv[2]))
            for i in results:
                utils.log(0, i + ': ' + str(results[i]))
    else:
        usage()
        exit(1)

if __name__ == '__main__':
    main()
