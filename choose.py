import random, sys
import utilities as utils

CIV_POOL = ["America","Arabia","Assyria","Austria","Aztecs","Babylon","Brazil","Byzantium","Carthage","Celts","China","Denmark","Netherlands","Egypt","England","Ethiopia","France","Germany","Greece","Huns","Incans","India","Indonesia","Iroquois","Japan","Maya","Mongolia","Morocco","Ottomans","Persia","Poland","Polynesia","Portugal","Rome","Russia","Shoshone","Siam","Songhai","Spain","Sweden","Venice","Zulus"]
CIV_BLACKLIST = [ 'Venice' ]

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

def pool_size():
    return len(CIV_POOL)

def draw_random_civ(remove_on_progress):
    if(pool_size() <= 0):
        raise GreedyPlayer()
    index = random.randint(0, pool_size() - 1)
    if(remove_on_progress): random_civ = CIV_POOL.pop(index)
    else: random_civ = CIV_POOL[index]

    if(random_civ in CIV_BLACKLIST):
        random_civ = draw_random_civ(remove_on_progress)
    return random_civ

def pChoose(players):
    return pChoosec(players, pool_size())

def pChoosec(players, civilizations):
    player_civs = {}
    remove_on_progress = False

    if(players <= 0 or civilizations <= 0):
        raise NonPositiverange()
    elif(civilizations > pool_size()):
        raise OverflowRange()
    elif((civilizations % players) == pool_size()):
        remove_on_progress = False

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

        if(argc == 1):
            utils.log(0, str(pChoose(int(sys.argv[1]))))
        elif(argc == 2):
            utils.log(0, str(pChoosec(int(sys.argv[1]), int(sys.argv[2]))))
        else:
            raise InvalidUsage()
    except InvalidUsage as e:
        utils.log(1, 'Throwing out input...')

if __name__ == '__main__':
    main()
