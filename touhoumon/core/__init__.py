import os.path

import move
import species
import typing
import touhoumon.resources

RESOURCES = os.path.dirname(touhoumon.resources.__file__)
SPECIES = os.path.join(RESOURCES, 'species.xml')
MOVES = os.path.join(RESOURCES, 'moves.xml')

MoveFactory = move.MoveFactory(MOVES)
SpeciesFactory = species.SpeciesFactory(SPECIES)
TypeChart = typing.TypeChart
