import operator

import touhoumon.core
import touhoumon.core.touhou

def index(app, req):
	""" Show interactive Touhoumon information view """

	if 'search' in req.form and req.form['search']:
		output = _evaluate_input(req.form['search'])
	else:
		output = ""

	return app.create_response(app.render_template('interactive-old',
		output=output))

def get_info(app, req):
	""" Evaluate POST query (search) and return type information """
	if 'search' not in req.form.keys():
		output = ''
	else:
		typename = req.form['search']
		output = _evaluate_input(typename)

	return app.create_response(output,
			content_type='text/plain')

def _evaluate_input(typename):
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
			return "\n'{0}' is neither a valid type nor a recognized Touhoumon name.\n".format(typename)
	
	output = [""]

	if species:
		output.append(str(species))
		output.append("HP: %(hp)s, Atk: %(atk)s, Def: %(def)s, SAtk: %(satk)s, "
				"SDef: %(sdef)s, Spd: %(spd)s" % species.get_base_stats())
	else:
		output.append("Typing: {0}".format(str(typing)))
	
	if len(typing) <= 2:
		output.append("\tDEFENSIVE STATS")
		for othertype, dmg in typing.get_def_multipliers().iteritems():
			if dmg > 1:
				output.append("Weak: {0} x {1}".format(str(othertype), dmg))
		for othertype, dmg in typing.get_def_multipliers().iteritems():
			if dmg < 1 and dmg > 0:
				output.append("Strong: {0} x {1}".format(str(othertype), dmg))
		for othertype, dmg in typing.get_def_multipliers().iteritems():
			if dmg == 0:
				output.append("Immune: {0} x {1}".format(str(othertype), dmg))

	# Sort damage by effectiveness
	off_stats = sorted(typing.get_off_multipliers().items(),
					key=operator.itemgetter(1), reverse=True)
	positive_coverage = len([stat for stat in off_stats if stat[1] >= 1])
	output.append("\tOFFENSIVE STATS ({0}/{1} coverage)".format(
		positive_coverage, len(off_stats)))

	for othertype, dmg in off_stats:
		if dmg > 1:
			output.append("Effective: {0} x {1}".format(str(othertype), dmg))
		elif dmg < 1:
			output.append("Weak: {0} x {1}".format(str(othertype), dmg))
	
	output.append("")

	return "\n".join(output)
