import operator

import touhoumon.core
import touhoumon.core.touhou

def index(app, req, search=None):
	""" Show interactive Touhoumon information view """

	if 'search' in req.form and req.form['search']:
		# If the page was called via POST
		output = _evaluate_input(app, req.form['search'])
	elif search:
		output = _evaluate_input(app, search)
	else:
		output = ""

	# Build list of names for auto-completion
	completionNames = \
			[ species.get_name() for species
				in touhoumon.core.SpeciesFactory.get_all_species() ] + \
			[ typing.get_name() for typing
				in touhoumon.core.TypeChart.get_types() ]

	return app.create_response(app.render_template('interactive-main',
		completionNames=completionNames,
		output=output))

def get_info(app, req):
	""" Evaluate POST query (search) and return type information """
	if 'search' not in req.form.keys():
		output = ''
	else:
		typename = req.form['search']
		output = _evaluate_input(app, typename)

	return app.create_response(output,
			headers=[('Content-Type', 'text/html')])

def _evaluate_input(app, typename):
	try:
		# First, assume a type name was passed
		typing = (touhoumon.core.TypeChart.get_dual_type(typename)
				  if '/' in typename
				  else touhoumon.core.TypeChart.get_type(typename))
		species = None
	except:
		# Now, try Touhou names
		try:
			species = touhoumon.core.SpeciesFactory.get_species(typename)
			typing = species.get_typing()
		except:
			return "'{0}' is neither a valid type nor a recognized Touhoumon name.".format(typename)
	
	species_part = app.render_template('interactive-species',
		species=species, typing=typing)

	# Sort damage by effectiveness and exclude neutral attacks
	def_stats = filter(lambda stat: stat[1] != 1,
					sorted(typing.get_def_multipliers().items(),
						key=operator.itemgetter(1), reverse=True))
	off_stats = sorted(typing.get_off_multipliers().items(),
				key=operator.itemgetter(1), reverse=True)
	typing_count = len(off_stats)
	positive_coverage = len([stat for stat in off_stats if stat[1] >= 1])
	off_stats = filter(lambda stat: stat[1] != 1, off_stats)

	typing_part = app.render_template('interactive-typing',
		typing=typing, def_stats=def_stats,
		off_stats=off_stats, positive_coverage=positive_coverage,
		typing_count=typing_count)

	return species_part + '\n' + typing_part
