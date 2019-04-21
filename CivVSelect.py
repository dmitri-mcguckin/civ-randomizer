import random, sys
import utilities as utils

CIV_LIST = ["America","Arabia","Assyria","Austria","Aztecs","Babylon","Brazil","Byzantium","Carthage","Celts","China","Denmark","Netherlands","Egypt","England","Ethiopia","France","Germany","Greece","Huns","Incans","India","Indonesia","Iroquois","Japan","Maya","Mongolia","Morocco","Ottomans","Persia","Poland","Polynesia","Portugal","Rome","Russia","Shoshone","Siam","Songhai","Spain","Sweden","Venice","Zulus"]

def civ_len():
    return len(CIV_LIST)

def choose(numPlayers, numCivs):
    players = {}

    if(civ_len() < (numPlayers * numCivs)+1):
        utils.log(3, 'User tried to choose ' + str(numCivs) + ' from a pool of ' + str(civ_len()) + ' civs!' )
        return players

    def getCiv():
        i = random.randint(0, civ_len() - 1)
        civ = CIV_LIST.pop(i)
        if (civ == "Venice"):
            return None
        return civ

    for p in range(numPlayers):
        extra = False
        civs = []
        for i in range(numCivs):
            new_civ = getCiv()
            if(new_civ == None):
                extra = True
            civs.append(new_civ)
        if extra:
            getCiv()
        players[p] = civs
    return players

def main():
    utils.log(0, str(choose(int(sys.argv[1]), 10)))

if __name__ == '__main__':
    main()
