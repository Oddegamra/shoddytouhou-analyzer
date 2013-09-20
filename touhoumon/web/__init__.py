import os.path

import mako.template
import mako.lookup

import view

def get_view_template(name):
	basedir = os.path.dirname(view.__file__)
	lookup = mako.lookup.TemplateLookup(directories=[basedir])
	tmpl = mako.template.Template(filename=os.path.join(basedir, name + ".tmpl"), lookup=lookup)
	return tmpl
