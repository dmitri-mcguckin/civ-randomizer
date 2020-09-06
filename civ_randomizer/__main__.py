import sys
import logging
import argparse
import civ_randomizer as cr
from civ_randomizer.bot import CivRandomizerBot
from civ_randomizer.randomizer import Randomizer


def main():
    parser = argparse.ArgumentParser(prog=cr.BOT_NAME,
                                     description=cr.BOT_DESCRIPTION,
                                     allow_abbrev=False)
    parser.add_argument('-o', '--one-shot',
                        dest='one_shot',
                        action='store_true',
                        default=False,
                        help='Only run the randomizer and not the Discord bot.')
    parser.add_argument('--num-players', '--np',
                        dest='num_players',
                        type=int,
                        required='-o' in sys.argv,
                        help='[One Shot Only] Number of players for the randomizer.')
    parser.add_argument('--num-civs-per-player', '--ncpp',
                        dest='num_civs_per_player',
                        type=int,
                        default=1,
                        help='[One Shot Only] Number of civilizations per player for the randomizer.')
    parser.add_argument('--player-names', '-pn',
                        dest='player_names',
                        nargs='+',
                        default=None,
                        help='[One Shot Only] List of optional player names to map to selections. (The number of names must match the number of players or else this will be ignored).')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='Enable verbose output.')
    args = parser.parse_args()

    if(args.verbose):
        cr.BOT_LOG_LEVEL = logging.DEBUG

    if(args.one_shot):
        profile = cr.load_dict_from_json(cr.DEFAULT_PROFILE_ASSET)
        r = Randomizer(profile)
        selection = r.choose(args.num_players,
                             num_civs_per_player=args.num_civs_per_player,
                             player_names=args.player_names)

        for name, civs in selection.items():
            print('{}:'.format(name.title()))
            for civ in civs:
                print('\t{}'.format(str(civ).title()))
    else:
        bot = CivRandomizerBot(description=cr.BOT_DESCRIPTION)

        try:
            bot.run(cr.BOT_TOKEN)
        except KeyboardInterrupt:
            cr.LOG.warn('Got interrupt signal!')
        finally:
            bot.stop()


if __name__ == '__main__':
    main()
