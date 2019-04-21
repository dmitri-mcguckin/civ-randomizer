#
# Local utility stuff
#
def log(arg_mode, message):
    mode = {
            0: 'INFO',
            1: 'WARN',
            2: 'DEBUG',
            3: 'ERROR'
        }

    print('[' + mode[arg_mode] + ']: ' + message)
