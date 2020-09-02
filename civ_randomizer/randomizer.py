import copy
import random


class Civilization:
    def __init__(self, name: str, aliases: [str] = []):
        self.name = name
        self.aliases = aliases

    def __lt__(self, civ):
        if(isinstance(civ, Civilization)):
            return self.name.lower() < civ.name.lower()
        elif(isinstance(civ, str)):
            return self.name.lower() < civ.lower()
        else:
            return False

    def __eq__(self, civ):
        if(isinstance(civ, Civilization)):
            return self.name.lower() == civ.name.lower()
        elif(isinstance(civ, str)):
            return civ.lower() in self.name.lower()
        else:
            return False

    def __ne__(self, civ):
        if(isinstance(civ, Civilization)):
            return self.name.lower() != civ.name.lower()
        elif(isinstance(civ, str)):
            return civ.lower() not in self.name.lower()
        else:
            return True

    def __str__(self):
        return self.name

    def __repr__(self):
        aka = 'aka ' + ', '.join(self.aliases) \
              if len(self.aliases) > 0 else 'No aliases'
        return "<Civilization {} ({})>" \
               .format(self.name, aka)


class DLC:
    def __init__(self, name: str, details: dict):
        self.name = name
        self.civilizations = []

        for key, value in details.items():
            if(key == 'civilizations'):
                self.civilizations = Randomizer.generate_civilizations(value)
            else:
                setattr(self, key, value)

    def __repr__(self):
        return "<DLC {} civilizations={}>".format(self.name,
                                                  self.civilizations)

    def to_dict(self):
        civilizations = {}

        for civ in self.civilizations:
            civilizations[civ.name] = civ.aliases

        return {
            'enabled': self.enabled,
            'civilizations': civilizations
        }


class Randomizer:
    def __init__(self, profile: dict):
        # Randomizer defaults to guarentee that these fields exist
        #   if the profile fails to populate them
        self.civilizations = []
        self.dlc_packs = []
        self.profile = None

        # Load the given profile
        self._load_profile(profile)

    def __str__(self):
        return "<Randomizer {} civilizations, {} blacklisted, {} dlcs>" \
               .format(len(self.civilizations),
                       len(self.blacklist),
                       len(self.dlc_packs))

    def _load_profile(self, profile: dict) -> None:
        """
        Setup the randomizer with the given profile

        Parameters
        ----------
        profile: `dict` A raw python dictionary with the current civ configs.
        """
        # Process the raw profile into fields and values
        for key, value in profile.items():
            if(key == 'civilizations'):
                self.civilizations = Randomizer.generate_civilizations(value)
            elif(key == 'dlc_packs'):
                self.dlc_packs = Randomizer.generate_dlc(value)
            else:
                setattr(self, key, value)

    def to_dict(self) -> dict:
        """
        Turns the current randomizer into a python dictionary.

        Returns
        -------
        `dict`: All of the randomizer configuration in dictionary form.
        """
        dlcs = {}
        for dlc in self.dlc_packs:
            dlcs[dlc.name] = dlc.to_dict()

        civs = {}
        for civ in self.civilizations:
            civs[civ.name] = civ.aliases

        return {
            'blacklist': self.blacklist,
            'civilizations': civs,
            'dlc_packs': dlcs
        }

    def choose(self,
               num_players: int,
               num_civs_per_player: int = 1,
               player_names: [str] = None) -> dict:
        """
        Randomly chooses a specified of civilizations per specified number of players.

        This executes a round-robin choosing algorithm, wherein each player takes turns choosing their next civ. (given only 2 players: player 1 chooses, player 2 chooses, player 1 chooses, etc.)

        Parameters
        ----------
        num_players: `int` The number of players to draft civilizations for.
        num_civs_per_player: `int` The number of civilizations to draft per player.
        player_names: '[str]' An optional list of names to map onto the selection output.

        Returns
        -------
        `dict` A dictionary of players each containing their own unique draft of civilizations.

        Raises
        ------
        `ValueError`: This is raised iff the function detects that there is are more civilizations expected to choose from than are in the pool.
        """
        # Load the civilization pool
        players = {}
        pool = copy.deepcopy(self.civilizations)

        # Load the DLCS
        for dlc in self.dlc_packs:
            if(dlc.enabled):
                pool += dlc.civilizations

        # Filter the pool by blacklist
        for civ in pool:
            if civ in self.blacklist:
                pool.remove(civ)

        # Mathematical insurance that enough civs exist
        if((num_players * num_civs_per_player) > len(pool)):
            raise ValueError('Not enough civilizations for everyone.')

        # Initialize the players
        names = []
        for i in range(num_players):
            if(player_names is not None and len(player_names) == num_players):
                name = player_names[i]
            else:
                name = "Player #{}".format(i + 1)
            names.append(name)
            players[name] = []

        # Do the random selection
        for _ in range(num_civs_per_player):
            for i in range(num_players):
                new_civ = pool[random.randint(0, len(pool) - 1)]
                players[names[i]] += [new_civ]
                pool.remove(new_civ)
        return players

    def generate_civilizations(civs: dict) -> [Civilization]:
        """
        Converts a raw python dictionary of civilization data to an array of Civilization objects

        Parameters
        ----------
        civs: `dict` The raw civilization data to be processed.

        Returns
        -------
        `[Civilization]`: The array of succesfully processed civilizations.
        """
        civilizations = []
        for name, aliases in civs.items():
            civilizations.append(Civilization(name, aliases))
        return civilizations

    def generate_dlc(dlcs: dict) -> [DLC]:
        """
        Converts a raw python dictionary of dlc data to an array of DLC objects

        Parameters
        ----------
        dlcs: `dict` The raw dlc data to be processed.

        Returns
        -------
        `[DLC]`: The array of succesfully processed dlcs.
        """
        new_dlcs = []
        for name, details in dlcs.items():
            new_dlcs.append(DLC(name, details))
        return new_dlcs
