import json


def load_config(filename: str):
    with open(filename, 'r') as file:
        return json.loads(file.read())


def save_config(filename: str, data: dict):
    with open(filename, 'w+') as file:
        file.write("{}\n".format(json.dumps(data,
                                            allow_nan=True,
                                            indent=4,
                                            check_circular=True)))


def bot_config_factory() -> dict:
    return {
        'prefix': 'c!'
    }
