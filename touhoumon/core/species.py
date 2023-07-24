import xml.etree.ElementTree

from touhoumon.core.typing import TypeChart

class SpeciesFactory(object):
	""" Creates a Touhou species object from a name string. """

	def __init__(self, species_xml):
		""" @param species_xml: File-like object or file name (species.xml) """
		self.species_info = xml.etree.ElementTree.parse(species_xml)
		
		self.species = {}
		for species in self.species_info.getroot():
			if species.tag == 'species':
				self.species[species.attrib['name'].lower()] = Species(species)

	def get_all_species(self):
		return list(sorted(iter(self.species.values()), key=lambda s: s.get_id()))

	def get_species(self, name):
		lower_name = name.lower()
		if lower_name in self.species:
			return self.species[lower_name]
		elif (lower_name.startswith('c') and
			  'chibi ' + lower_name[1:] in self.species):
			return self.species['chibi ' + lower_name[1:]]
		elif (lower_name.startswith('a') and
			  'attack ' + lower_name[1:] in self.species):
			return self.species['attack ' + lower_name[1:]]
		elif (lower_name.startswith('d') and
			  'defense ' + lower_name[1:] in self.species):
			return self.species['defense ' + lower_name[1:]]
		elif (lower_name.startswith('t') and
			  'technical ' + lower_name[1:] in self.species):
			return self.species['technical ' + lower_name[1:]]
		elif (lower_name.startswith('h') and
			  'helper ' + lower_name[1:] in self.species):
			return self.species['helper ' + lower_name[1:]]
		elif (lower_name.startswith('s') and
			  'speed ' + lower_name[1:] in self.species):
			return self.species['speed ' + lower_name[1:]]
		elif (lower_name.startswith('z') and
			  'zombie ' + lower_name[1:] in self.species):
			return self.species['zombie ' + lower_name[1:]]
		elif (lower_name.startswith('ad') and
			  'advent ' + lower_name[2:] in self.species):
			return self.species['advent ' + lower_name[2:]]
		else:
			raise Exception("Species {0} could not be found.".format(name))

class Species(object):
	""" A Touhou species. """

	def __init__(self, species_xml):
		""" @param species_xml XML element for this species. """
		self.info = species_xml

	def get_name(self):
		return self.info.attrib["name"]

	def get_id(self):
		return int(self.info.attrib["id"])

	def get_typing(self):
		typenames = self.info.findall("type")

		if len(typenames) == 1:
			return TypeChart.get_type(typenames[0].text)
		else:
			return TypeChart.get_dual_type([type.text for type in typenames])

	def get_base_stats(self):
		basestats = self.info.find("stats")
		stat = {}
		for base in basestats:
			if base.tag == "base":
				stat[base.attrib["stat"]] = int(base.text)

		return stat

	def get_moveset(self):
		movegroups = self.info.iter("moves")
		moves = []
		for group in movegroups:
			moves.extend([(move.text, group.attrib["origin"]) for move in group.findall("move")])
		return moves

	def has_move(self, movename):
		for move, origin in self.get_moveset():
			if movename.lower() == move.lower():
				return True

		return False

	def __repr__(self):
		return "Species: {0} ({1})".format(self.get_name(),
				                           str(self.get_typing()))
