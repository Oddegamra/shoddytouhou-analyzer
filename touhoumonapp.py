#!/usr/bin/env python3
import os.path
import urllib.parse
import mako.template
import mako.lookup
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import responder
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string

import touhoumon.web.view


class TouhoumonApp(object):
	""" Main web application object. This class dispatches requests
	by comparing them to the registered routes, and calling route
	endpoints when an request matches the route. """

	def __init__(self):
		self.urls = Map([
			# Every endpoint is a module within touhoumon.web.controller
			Rule('/touhou/',
				endpoint='analyze:index'),
			Rule('/touhou/analyze/'
				, endpoint='analyze:analyze'),
			Rule('/touhou/interactive/',
				endpoint='interactive:index'),
			Rule('/touhou/interactive/info',
				endpoint='interactive:get_info'),
			Rule('/touhou/interactive/<path:search>',
				endpoint='interactive:index'),
			Rule('/touhou/interactive-old/',
				endpoint='interactiveold:index'),
			Rule('/touhou/interactive-old/info',
				endpoint='interactiveold:get_info')
		])
		self.make_url = None  # This is created when a request is dispatched
		# Base URL for media files
		self.media = 'https://maya.sector-5.net/media/touhoumon/'
		# Base URL for THPP wiki links
		self.thppwiki = 'https://thpp.supersanctuary.net/wiki/'

	def dispatch_request(self, request):
		""" Dispatches the request to an appropriate controller function
		based on its endpoint resolved as module/function. """
		try:
			adapter = self.urls.bind_to_environ(request.environ)
			endpoint, values = adapter.match()
			func = import_string('touhoumon.web.controller.' + endpoint)
			self.make_url = adapter.build
			# Each controller function returns a Response object
			# (they usually call create_response)
			return func(self, request, **values)
		except HTTPException as e:
			return e

	def get_template(self, name):
		""" Retrieves the template matching <name> from the view
		directory. """
		basedir = os.path.dirname(touhoumon.web.view.__file__)
		lookup = mako.lookup.TemplateLookup(directories=[basedir])
		tmpl = mako.template.Template(filename=os.path.join(basedir,
			name + ".tmpl"), lookup=lookup)
		return tmpl

	def render_template(self, name, **kwargs):
		""" Returns the rendered template <name> with the inserted
		arguments. Also inserts a few default values into the
		template context, such as make_url. """
		tmpl = self.get_template(name)
		return tmpl.render(make_url=self.make_url,
                join_url=urllib.parse.urljoin,
                media=self.media,
				thppwiki=self.thppwiki,
				**kwargs)

	def create_response(self, content, *args, **kwargs):
		""" Creates a Response object with the specified <content>.
		The remaining <args> are passed to the Response constructor. """
		if 'content_type' not in kwargs:
			kwargs['content_type'] = 'text/html; charset=utf-8'
		return Response(content, *args, **kwargs)

	@responder
	def __call__(self, environ, start_response):
		""" When this class is called as function by the WSGI wrapper.
		Start dispatching and return response. """
		request = Request(environ)
		return self.dispatch_request(request)


if __name__ == '__main__':
	# Starts a local development server if run directly
	from werkzeug.serving import run_simple
	app = TouhoumonApp()
	run_simple('localhost', 5000, app, use_debugger=True,
				use_reloader=True)
