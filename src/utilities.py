import json

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
    file = open(file_path, mode='w+')
    file.write(data)
    file.close()

    return dictionary
