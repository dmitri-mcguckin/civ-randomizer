import operator as op
from functools import reduce

DEBUG = False
DELETE_AFTER_PROCESS = False

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer / denom

def flatten_list(list):
    result = []
    for sublist in list:
        if(type(sublist).__name__ == 'list'):
            for item in sublist:
                result.append(item)
        else:
            result.append(sublist)
    return result

def log(arg_mode, message):
    mode = {
            0: 'INFO',
            1: 'WARN',
            2: 'DEBUG',
            3: 'ERROR'
        }

    print('[' + mode[arg_mode] + ']: ' + message)
