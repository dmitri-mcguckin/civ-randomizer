import operator as op
import json
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

def load_json(file_path):
    # Read the raw JSON data
    file = open(file_path)
    file_data = file.read()
    file.close()

    # Transpose raw JSON into dictionary, store it in the object instance
    return json.loads(file_data)

def dump_json(file_path, dictionary):
    # Transpose dictionary into raw JSON
    data = json.dumps(dictionary, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=2, separators=None, default=None, sort_keys=True)

    # Write the raw JSON data to the specified file
    file = open(file_path, mode="w+")
    file.write(data)
    file.close()

    return dictionary

def main():
    os.symlink("../bin/civ-bot.sh", "./civ-bot")

if __name__ == '__main__':
    main()
