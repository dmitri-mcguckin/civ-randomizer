import argparse
import civ_randomizer as cr
from civ_randomizer.bot import Bot


def main():
    parser = argparse.ArgumentParser(prog=cr.BOT_NAME,
                                     description=cr.BOT_DESCRIPTION,
                                     allow_abbrev=False)
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='Enable verbose output')
    # args = parser.parse_args()

    bot = Bot()
    try:
        bot.run(cr.BOT_TOKEN)
    except KeyboardInterrupt:
        bot.stop()


if __name__ == '__main__':
    main()
