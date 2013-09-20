import os
import tempfile

import touhoumon.core
import touhoumon.core.touhou

def index(app, req):
	""" Upload a team file """

	return app.create_response(app.render_template('analyze-upload'))

def analyze(app, req):
	""" Analyze file uploaded in req. """
	if 'teamfile' not in req.files:
		return index(app, req)
	handle, filename = tempfile.mkstemp(suffix='touhou', text=True)
	content = req.files['teamfile'].stream.read()
	req.files['teamfile'].close()
	os.write(handle, content)
	os.close(handle)
	
	try:
		reader = touhoumon.core.touhou.TeamReader(filename, touhoumon.core.SpeciesFactory,
				                                  touhoumon.core.MoveFactory)
		team = reader.get_team()
		return app.create_response(app.render_template('analyze-show', team=team,
									off_coverage=team.get_offensive_coverage(),
		                            def_weakness=team.get_defensive_weaknesses(),
									def_strengths=team.get_defensive_strengths(),
									stats=team.get_cumulative_base_stats()))
	except:
		return error(app, req, 'Could not parse team file. Invalid or unrecognized file format. '
				          'Make sure to upload only team files created by Shoddy Touhoumon.')
	finally:
		os.unlink(filename)

def error(app, req, message='Undefinied error'):
	""" Show error message. """
	return app.create_response(app.render_template('error', errormessage=message))
