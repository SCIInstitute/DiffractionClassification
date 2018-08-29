class spacegroups:
	
	def __init__(self):

		groups = []
		families = []
		sgs = []
		geni = []

		with open("HSGdict.txt", 'r') as proto:
			for line in proto.readlines():
				group, family, sg, genus = line.strip().split(' ')
				
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
		self.sgs_to_group = dict(zip(sgs,groups))

		self.genus = set(geni)

		edges_genus = {"triclinic":[1,2],
						"monoclinic":[3,6],
						"orthorhombic":[7,9],
						"tetragonal":[10,16],
						"trigonal":[17,21],
						"hexagonal":[22,27],
						"cubic":[28,32]}

		edges_species = {1:[1,1],
						2:[2,2],
						3:[3,5],
						4:[6,9],
						5:[10,10],
						6:[11,15],
						7:[16,24],
						8:[25,46],
						9:[47,74],
						10:[75,80],
						11:[81,82],
						12:[83,88],
						#13:[89,98],
						14:[99,110],
						15:[111,122],
						16:[123,142],
						17:[143,146],
						18:[147,148],
						19:[149,155],
						20:[156,161],
						21:[162,167],
						22:[168,173],
						23:[174,174],
						24:[175,176],
						25:[177,186],
						26:[187,190],
						27:[191,194],
						28:[195,199],
						29:[200,206],
						30:[207,214],
						31:[215,220],
						32:[221,230]}

		self.edges = {"genus":edges_genus,
					  "species":edges_species}