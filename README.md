# Civilization Randomizer

A Discord bot for randomly selecting a subset of civs from all that's available in `Sid Meyer's Civilization V`, *(including all DLC's)* to make multiplayer with your friends spicy.

This bot is an alternative to the default in-game randomization that the base game provides. Instead of only randomly choosing one civ, at the start and not knowing what you have until you load into the game, you can now choose from a subset of civs. This bot enables friend groups to to team picking/fighting in a more interesting way as well as draft picking, (both teams alternate banning, then random pools are chosen, both teams alternate choosing).

# End-User *(Client)* Stuff

### Discord client commands:

* help: Stop it, get some help!
* civs: Displays the full list of civilizations in finer detail.
* blacklist: Displays the list of banned civilizations.
* ban: Bans specified civilizations.
* unban: Unbans specified civilizations.
* choose: Creates a randomized ist for <player count> number of players with <civilizations per player> civs per layer.
* dlcs: Displays the list of Civilization V DLC's and their details.
* enable: Enables the specified DLC.
* disable: Disables the specified DLC.

### Example commands:

Ban all civs:
* $ `c!ban all`

Ban Poland
* $ `c!ban polish`

\**Civs can be refered to by their aliases as well as their primary names when executing any command, see `c!civs` to checkout all the civ aliases.*

Ban Poland then America
* $ `c!ban poland USA`

\**Multiple civs can be banned or unbanned in one command by simply separating the civ names by space.*

Unban all civs:
* $ `c!unban all`

Disable dlc containing the keyword *"Korea"*
* $ `c!disable korea`

\**The keywords for disabling specific DLC's are case insensitive*

Enable dlc containing the keywords "Double Civilization"
* $ `c!enable "double civilization"`

Enable the dlc's containing the keywords "Korea" then "Double Civilization"
* $ `c!enable korea "double civilization"`

\**Multiple DLC's can be enabled or disabled in one command by simply separating your keywords by space. If you'd like to have multiple keywords go to one search, be sure to encapsulate them with \" \" (quotations)*

# Admin *(Server)* Stuff

### Supported platforms:

 * Linux
 * Windows*

\**The installer scripts are not directly supported on this platform and will likely need to by emulated via CYGWIN OR MINGWIN. This is explicitly because the bot follows the `/opt`, `/var`, `/log` conventions for storing and retrieving configs, logs, etc.*

### Installation:

A set of installation scripts have been provided for your convenience.

1. $ `cd ./civ-randomizer/bin`
2. $ `sudo ./install.sh`

Afterwards, the bot is installed to `/opt/civ-bot` and some symlinks are created in `/usr/bin` so you can simply run `civ-bot` for the discord server and `civ-choose` for a one-time-runtime civ-randomizer anywhere on your system.

### Local choose mechanism:

This is a program that is a part of the bot already but can be run separate from the bot, *(a-la-carte)*. A soft link to the choose script is already provided for you in your `/bin` folder, so you can run the program as-is after installation.

`civ-choose [<Int> Player Count] [(optional) <Int> Civilizations per Player]`

### Discord bot server:

No arguments are needed for the server binary to run. however, an environment variable named `CIV_BOT_TOKEN` must exist on your system before starting the bot and it must have a valid Discord auth token that you can get from the [Discord Developer Portal](https://discordapp.com/developers/applications/).

`civ-bot`

*(for persistence, use the following)*

`screen -dmS civ-bot civ-bot`
