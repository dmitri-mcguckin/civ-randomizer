# Civilization Randomizer

A python bot for randomly selecting a subset of all civs in `Sid Meyer's Civilization V`, *(including all DLC's)*, to choose from.

# Usage

### Supported platforms:

 * Linux
 * Windows*

\*The installer scripts are not directly supported on this platform and will likely need to by emulated via CYGWIN OR MINGWIN. This is explicitly because the bot follows the `/opt`, `/var`, `/log` conventions for storing and retrieving configs, logs, etc.

### Installation

A set of installation scripts have been provided for your convenience.

1. $ `cd ./civ-randomizer/bin`
2. $ `sudo ./install.sh`

Afterwards, the bot is installed to `/opt/civ-bot` and some symlinks are created in `/usr/bin` so you can simply run `civ-bot` for the discord server and `civ-choose` for a one-time-runtime civ-randomizer anywhere on your system.

### Local choose mechanism

`civ-choose [<Int> Player Count] [<Int> Civilizations per Player]`

### Discord bot

`civ-bot`

*(for persistence, use the following)*

`screen -dmS civ-bot civ-bot`
