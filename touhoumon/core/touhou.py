import xml.etree.ElementTree

from touhoumon.core.typing import TypeChart

class TeamReader(object):
	""" Creates a Touhou team from a Shoddy2 save file. """

	def __init__(self, team_xml, species_factory, move_factory):
		""" @param team_xml: File-like object or file name """
		self.team_info = xml.etree.ElementTree.parse(team_xml)
		self.species_factory = species_factory
		self.move_factory = move_factory

	def get_team(self):
		team = Team()
		for touhou in self.team_info.getroot():
			if (touhou.tag == "pokemon"):
				team.add_member(Touhou(touhou, self.species_factory,
					                   self.move_factory))

		return team

	def get_touhou(self, name):
		team = self.get_team()
		for touhou in team.get_members():
			if touhou.get_name().lower() == name.lower():
				return touhou

		raise Exception("Move {0} could not be found.".format(name))

class Team(object):
	def __init__(self):
		self.touhous = []

	def add_member(self, touhou):
		self.touhous.append(touhou)

	def get_members(self):
		""" Returns a list of all Touhous in a team. """
		return self.touhous

	def get_offensive_coverage(self):
		types = []
		for type in TypeChart.get_types():
			strong = []
			weak = []
			neutral = []
			for touhou in self.get_members():
				# Transfer to dictionary
				covering = touhou.get_offensive_coverage()

				if type in covering and covering[type] > 1.0:
					strong.append(touhou)
				elif type in covering and covering[type] < 1.0:
					weak.append(touhou)
				else:
					neutral.append(touhou)

			if strong:
				types.append((type, 'Strong', strong))
			elif not strong and neutral:
				types.append((type, 'Neutral', neutral))
			else:
				types.append((type, 'Weak', weak))

		return types

	def get_defensive_weaknesses(self):
		types = []
		for type in TypeChart.get_types():
			weak = []

			for touhou in self.get_members():
				defensive = touhou.get_typing().get_def_multipliers()[type]
				if defensive > 1.0:
					weak.append(touhou)

			types.append((type, weak))
	
		return types

	def get_defensive_strengths(self):
		types = []
		for type in TypeChart.get_types():
			strong = []

			for touhou in self.get_members():
				defensive = touhou.get_typing().get_def_multipliers()[type]
				if defensive < 1.0:
					strong.append(touhou)

			types.append((type, strong))
	
		return types

	def get_cumulative_base_stats(self):
		stats = {}
		for touhou in self.get_members():
			touhou_stats = touhou.get_species().get_base_stats()

			for stat, val in touhou_stats.iteritems():
				if stat not in stats:
					stats[stat] = val
				else:
					stats[stat] += val

		return stats

	def __len__(self):
		return len(self.touhous)

	def __iter__(self):
		return self.touhous.__iter__()

class Touhou(object):
	""" A concrete Touhou. """

	def __init__(self, touhou_xml, species_factory, move_factory):
		""" @param touhou_xml: XML element for this Touhou. """
		self.info = touhou_xml
		self.species_factory = species_factory
		self.move_factory = move_factory
	
	def is_shiny(self):
		return self.info.find("shiny") is not None

	def get_name(self):
		nickname = self.info.find("nickname").text
		if nickname:
			return nickname
		else:
			return self.info.attrib["species"]

	def get_species(self):
		name = self.info.attrib["species"]
		return self.species_factory.get_species(name)

	def get_typing(self):
		return self.get_species().get_typing()

	def get_moves(self):
		moveset = self.info.find("moveset")
		moves = moveset.findall("move")
		return [self.move_factory.get_move(move.text) for move in moves]

	def get_defensive_weakness(self):
		""" Returns a list of strenghts/weaknesses of this Touhou.
		Numbers < 1 mean a strength, > 1 mean a weakness. """
		return [(type, self.get_typing().get_def_multipliers()[type])
			    for type in TypeChart.get_types()
				if self.get_typing().get_def_multipliers()[type] != 1.0]

	def get_offensive_coverage(self):
		""" Returns a dictionary of types this Touhou's moves are strong/weak against.
		Numbers < 1 mean a weakness, > 1 a strength. """
		if not self.get_moves():
			return []

		types = {}
		for move in self.get_moves():
			if not move.is_attack():
				continue

			move_effectiveness = move.get_typing().get_off_multipliers()

			for type, multiplier in move_effectiveness.iteritems():
				if (type not in types or
				    types[type] < multiplier):
					types[type] = multiplier

		return types

	def __repr__(self):
		return "Touhou: {0} ({1})".format(self.get_name(),
				                          str(self.get_typing()))
	
	def __str__(self):
		return self.get_name()
