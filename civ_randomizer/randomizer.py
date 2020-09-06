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
            name_match = civ.lower() in self.name.lower()
            alias_match = civ.lower() in list(map(lambda x: x.lower(), self.aliases))
            return name_match or alias_match
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

    def __lt__(self, dlc):
        if(isinstance(dlc, DLC)):
            return self.name.lower() < dlc.name.lower()
        elif(isinstance(dlc, str)):
            return self.name.lower() < dlc.lower()
        else:
            return False

    def to_dict(self):
        civilizations = {}

        for civ in sorted(self.civilizations):
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

        # The blacklist can be loaded only after the default and dlc civs
        #   have been loaded
        blacklist = profile.get('blacklist')
        if(blacklist is not None):
            self.blacklist = []
            for civ_name in blacklist:
                ban_civ = self.resolve_civ_name(civ_name)
                self.blacklist.append(ban_civ)

    def resolve_civ_name(self, civ_name: str) -> Civilization:
        # Search the vanilla civs for a match
        for civ in self.civilizations:
            if(civ == civ_name):
                return civ

        # Search the DLCs for a match
        for dlc in self.dlc_packs:
            for civ in dlc.civilizations:
                if(civ == civ_name):
                    return civ
        raise ValueError('Civilization {} not found'.format(civ_name))

    def to_dict(self) -> dict:
        """
        Turns the current randomizer into a python dictionary.

        Returns
        -------
        `dict`: All of the randomizer configuration in dictionary form.
        """
        blacklist = list(map(lambda x: x.name.title(), sorted(self.blacklist)))
        civs = {}
        for civ in sorted(self.civilizations):
            civs[civ.name] = civ.aliases

        dlcs = {}
        for dlc in sorted(self.dlc_packs):
            dlcs[dlc.name] = dlc.to_dict()

        return {
            'blacklist': blacklist,
            'civilizations': civs,
            'dlc_packs': dlcs
        }

    def generate_draft_pool(self) -> [Civilization]:
        """
        Creates the pool of civilizations to draft from. First it adds all of
        the default civs, then adds only enabled dlc civs, then it removes all
        of the blacklisted civs.

        Returns
        -------
        `[Civilization]`: A list of all of the unbanned and enabled
                          civilizations.
        """
        pool = copy.deepcopy(self.civilizations)

        # Load the DLCS
        for dlc in self.dlc_packs:
            if(dlc.enabled):
                pool += dlc.civilizations

        # Filter the pool by blacklist
        for civ in self.blacklist:
            if(civ in pool):
                pool.remove(civ)
        return sorted(pool)

    def choose(self,
               num_players: int,
               civs_per_player: int = 1,
               player_names: [str] = None) -> dict:
        """
        Randomly chooses a specified of civilizations per specified number of players.

        This executes a round-robin choosing algorithm, wherein each player takes turns choosing their next civ. (given only 2 players: player 1 chooses, player 2 chooses, player 1 chooses, etc.)

        Parameters
        ----------
        num_players: `int` The number of players to draft civilizations for.
        civs_per_player: `int` The number of civilizations to draft per player.
        player_names: '[str]' An optional list of names to map onto the selection output.

        Returns
        -------
        `dict` A dictionary of players each containing their own unique draft of civilizations.

        Raises
        ------
        `ValueError`: This is raised iff the function detects that there is are more civilizations expected to choose from than are in the pool.
        """
        # Create the player table and load the draft pool
        players = {}
        pool = self.generate_draft_pool()

        # Mathematical insurance that enough civs exist
        if((num_players * civs_per_player) > len(pool)):
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
        for _ in range(civs_per_player):
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

    def enable_all_dlc(self):
        for dlc in self.dlc_packs:
            dlc.enabled = True

    def disable_all_dlc(self):
        for dlc in self.dlc_packs:
            dlc.enabled = False

    def enable_dlc_by_name(self, name: str):
        found = False  # Variable for tracking if anything changed

        # Search all the DLCs for partial name match
        for dlc in self.dlc_packs:
            if(name.lower() in dlc.name.lower()):
                dlc.enabled = True
                found = True

        # If nothing was found, raise an exception so the bot can relay that
        #   info to the user
        if(not found):
            raise ValueError('DLC `{}` not found'.format(dlc))

    def disable_dlc_by_name(self, name: str):
        found = False  # Variable for tracking if anything changed

        # Search all the DLCs for partial name match
        for dlc in self.dlc_packs:
            if(name.lower() in dlc.name.lower()):
                dlc.enabled = False
                found = True

        # If nothing was found, raise an exception so the bot can relay that
        #   info to the user
        if(not found):
            raise ValueError('DLC `{}` not found'.format(dlc))
