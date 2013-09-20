import xml.etree.ElementTree

from touhoumon.core.typing import TypeChart

class MoveFactory(object):
	""" Creates a Touhou move object from a name string. """

	def __init__(self, move_xml):
		""" @param move_xml: File-like object or file name (moves.xml) """
		self.move_info = xml.etree.ElementTree.parse(move_xml)
		self.moves = {}
		for move in self.move_info.getroot():
			if (move.tag == "move"):
				self.moves[move.attrib["name"].lower()] = Move(move)

	def get_move(self, name):
		if name.lower() in self.moves:
			return self.moves[name.lower()]
		else:
			raise Exception("Move {0} could not be found.".format(name))

class Move(object):
	""" A Touhou move. """

	def __init__(self, move_xml):
		""" @param move_xml: XML element for this move. """
		self.info = move_xml

	def get_name(self):
		return self.info.attrib["name"]

	def get_typing(self):
		typename = self.info.find("type")
		try:
			return TypeChart.get_type(typename.text)
		except:
			# Typeless moves
			return None

	def get_target(self):
		return self.info.find("target").text

	def get_power(self):
		return int(self.info.find("power").text)

	def is_attack(self):
		return (self.get_target() in ("Non-user", "Enemies", "Others")
				and self.get_power() > 0)

	def __eq__(self, other):
		if isinstance(other, Move):
			return self.get_name() == other.get_name()
		elif isinstance(other, (str, unicode)):
			return self.get_name() == other
		else:
			return False

	def __repr__(self):
		return "Move: {0} ({1})".format(self.get_name(),
				                        str(self.get_typing()))
