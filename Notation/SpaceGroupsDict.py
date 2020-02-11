import os
dirname = os.path.dirname(__file__)
class spacegroups:
	
    def __init__(self):

        groups = []
        families = []
        sgs = []
        geni = []
        with open(os.path.join(dirname,"HSGdict.txt"), 'r') as proto:
            for line in proto.readlines():
                group, family, sg, genus = line.strip().split('\t')
                groups.append(group)
                families.append(family)
                sgs.append(sg)
                geni.append(genus)

        self.family_as_int = {}
        counter = 0
        for item in families:
            if item not in self.family_as_int.keys():
                counter += 1
                self.family_as_int[item] = counter


        self.group_to_family = dict(zip(groups,families))
        self.group_to_sgs = dict(zip(groups,sgs))
        self.group_to_geni = dict(zip(groups,geni))
        self.genera_to_family = dict(zip(geni,families))
        self.sgs_to_group = dict(zip(sgs,groups))
        self.sgs_to_genus = dict(zip(sgs,geni))
        self.genus = set(geni)

        edges_genus = {"triclinic":[1,2],
                        "monoclinic":[3,5],
                        "orthorhombic":[6,8],
                        "tetragonal":[9,15],
                        "trigonal":[16,20],
                        "hexagonal":[21,27],
                        "cubic":[28,32]}

        edges_species = {1:[1,1],
                        2:[2,2],
                        3:[3,5],
                        4:[6,9],
                        5:[10,15],
                        6:[16,24],
                        7:[25,46],
                        8:[47,74],
                        9:[75,80],
                        10:[81,82],
                        11:[83,88],
                        12:[89,98],
                        13:[99,110],
                        14:[111,122],
                        15:[123,142],
                        16:[143,146],
                        17:[147,148],
                        18:[149,155],
                        19:[156,161],
                        20:[162,167],
                        21:[168,173],
                        22:[174,174],
                        23:[175,176],
                        24:[177,182],
                        25:[183,186],
                        26:[187,190],
                        27:[191,194],
                        28:[195,199],
                        29:[200,206],
                        30:[207,214],
                        31:[215,220],
                        32:[221,230]}

        self.edges = {"genus":edges_genus,
                      "species":edges_species}

        self.sgs_to_family = {}
        for family in self.edges["genus"].keys():
            startstop = self.edges['genus'][family]
            
            for genera in range(startstop[0],startstop[1]+1):
                ss = self.edges["species"][genera]
                for sgroup in range(ss[0],ss[1]+1):
                    self.sgs_to_family[sgroup] = self.family_as_int[family]

