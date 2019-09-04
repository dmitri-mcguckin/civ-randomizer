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

    def __repr__(self): return "{ Name: " + self.name + "\tEnabled: " + str(self.enabled) + ",\tis_dlc: " + str(self.is_dlc) + ",\talternate_names: " + str(self.alternate_names) + " }"

    def __str__(self): return "{ Name: " + self.name + "\tEnabled: " + str(self.enabled) + ",\tis_dlc: " + str(self.is_dlc) + ",\talternate_names: " + str(self.alternate_names) + " }"

def main():
    c1_name = "rOmE"
    c1_alts = ['roman', 'romans']
    c2_name = "vEnIce"
    c2_alts = ['venician', 'venicians']

    c1 = Civilization(c1_name, c1_alts, True)
    c2 = Civilization(c2_name, c2_alts)

    print("Civs:\n" + str(c1) + "\n" + str(c2))

    print("\n(c1 == rome): " + str(c1 == "rome"))
    print("(c1 != rome): " + str(c1 != "rome"))

    print("\n(c2 == venice): " + str(c2 == "venice"))
    print("(c2 != venice): " + str(c2 != "venice"))

    print("\n(c1 == c2): " + str(c1 == c2))
    print("(c1 != c2): " + str(c1 !=  c2))

if __name__ == "__main__":
    main()
