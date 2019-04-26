import random, sys, math, json
import utilities as utils

CONFIG='./config.json'

class GreedyPlayer(Exception):
    def __init__(self):
        utils.log(3, 'User did not allow enough civs to share!')

class NonPositiverange(Exception):
    def __init__(self):
        utils.log(3, 'User tried to enter a non-positive range!')

class OverflowRange(Exception):
    def __init__(self):
        utils.log(3, 'User tried to enter a pool size bigger than the number of available civilizations!')

class InvalidUsage(Exception):
    def __init__(self):
        utils.log(3, 'Invalid usage!\n\tUsage: python3 choose.py <[Int] player pool size> <[Int] civilization pool size>')

class CivRandomizer():
    def __init__(self):
        self.civilizations = JSON.

def reset_pool():
    CIV_POOL = DEFAULT_CIV_POOL

def pool_size():
    return len(CIV_POOL)

def recommended_pool_size(players):
    return math.floor(pool_size() / int(players)) - 1

def draw_random_civ(remove_on_progress):
    index = random.randint(0, pool_size() - 1)
    if(remove_on_progress): random_civ = CIV_POOL.pop(index)
    else: random_civ = CIV_POOL[index]

    if(random_civ in CIV_BLACKLIST):
        random_civ = draw_random_civ(remove_on_progress)
    return random_civ

def pChoose(players):
    return pChoosec(players, recommended_pool_size(players))

def pChoosec(players, civilizations, remove_on_progress=True):
    player_civs = {}

    if(players <= 0 or civilizations <= 0):
        raise NonPositiverange()
    elif(civilizations > pool_size()):
        raise OverflowRange()
    elif(((players * civilizations) + 1) > pool_size()):
        raise GreedyPlayer()

    for i in range(0, players):
        random_civs = []
        for j in range(0, (civilizations)):
            random_civs.append(draw_random_civ(remove_on_progress))
        player_civs[i] = random_civs
    return player_civs

def main():
    try:
        argc = len(sys.argv) - 1
        utils.log(2, 'ARGS: ' + str(sys.argv) + '\tARG COUNT: ' + str(argc))

        try:
            if(argc == 1):
                results = pChoose(int(sys.argv[1]))
            elif(argc == 2):
                results = pChoosec(int(sys.argv[1]), int(sys.argv[2]))
            else:
                raise InvalidUsage()
        except GreedyPlayer:
            utils.log(3, 'User attempted to choose from a pool of civs too big to share with all players.'
                + '\n\tRecommended size is: ' + str(recommended_pool_size(sys.argv[1])))
            exit(1)

        for i in results.keys():
            utils.log(0, 'Player ' + str(i + 1) + ': ' + str(results[i]))

    except InvalidUsage as e:
        utils.log(1, 'Throwing out input...')

if __name__ == '__main__':
    main()
