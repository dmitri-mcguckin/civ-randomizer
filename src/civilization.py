class Civilization():
    def __init__(self, name, alternate_names=[], is_dlc=False, enabled=True):
        if(name == None): raise ValueError('Civilization name cannot be null!')
        self.name = name
        self.alternate_names = alternate_names
        self.is_dlc = is_dlc
        self.enabled = enabled

        # Reformat the name(s) of the civilization
        self.name = self.name.title()
        for i in range(0, len(self.alternate_names)): self.alternate_names[i] = self.alternate_names[i].title()

    def __eq__(self, other_civ):
        if(isinstance(other_civ, str)): return (self.name == other_civ.title() or other_civ.title() in self.alternate_names)
        elif(isinstance(other_civ, Civilization)): return (self.name == other_civ.name.title() or other_civ.name.title() in self.alternate_names)

    def __ne__(self, other_civ):
        if(isinstance(other_civ, str)): return (self.name != other_civ.title() and not (other_civ.title() in self.alternate_names))
        elif(isinstance(other_civ, Civilization)): return (self.name != other_civ.name.title() and not (other_civ.name.title() in self.alternate_names))

    def __lt__(self, other_civ):
        if(isinstance(other_civ, str)): return (self.name < other_civ.title())
        elif(isinstance(other_civ, Civilization)): return (self.name < other_civ.name.title())

    def __le__(self, other_civ):
        if(isinstance(other_civ, str)): return (self.name <= other_civ.title())
        elif(isinstance(other_civ, Civilization)): return (self.name <= other_civ.name.title())

    def __gt__(self, other_civ):
        if(isinstance(other_civ, str)): return (self.name > other_civ.title())
        elif(isinstance(other_civ, Civilization)): return (self.name > other_civ.name.title())

    def __ge__(self, other_civ):
        if(isinstance(other_civ, str)): return (self.name >= other_civ.title())
        elif(isinstance(other_civ, Civilization)): return (self.name >= other_civ.name.title())

    def __repr__(self): return self.name + ": Enabled(" + str(self.enabled) + "), Is DLC(" + str(self.is_dlc) + "), Alternate names(" + str(self.alternate_names) + ")"
    def __str__(self):  return self.name + ": Enabled(" + str(self.enabled) + "), Is DLC(" + str(self.is_dlc) + "), Alternate names(" + str(self.alternate_names) + ")"
