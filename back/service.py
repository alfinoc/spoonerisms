from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest
from jinja2 import Environment, FileSystemLoader
from json import loads, dumps

from persistent import RedisStore

class SpoonerismService(object):

   def get_random(self, request):
      return self.render_template('random.html')

   def get_archive(self, request):
      return Response('a okay!')

   def get_submit(self, request):
      return Response('a okay!')

   def get_screen(self, request):
      return Response('a okay!')

   def get_about(self, request):
      return Response('a okay!')

   """
   dispatch requests to appropriate functions above
   """
   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/', endpoint='random'),
         Rule('/archive', endpoint='archive'),
         Rule('/about', endpoint='about'),
         Rule('/submit', endpoint='submit'),
         Rule('/screen', endpoint='screen'),
         Rule('/<all>', redirect_to=''),
      ])
      self.store = RedisStore()
      self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                   autoescape=True)

   def render_template(self, template_name, **context):
      t = self.jinja_env.get_template(template_name)
      return Response(t.render(context), mimetype='text/html')

   def wsgi_app(self, environ, start_response):
      request = Request(environ);
      response = self.dispatch_request(request);
      return response(environ, start_response);

   def __call__(self, environ, start_response):
      return self.wsgi_app(environ, start_response)

   def dispatch_request(self, request):
      adapter = self.url_map.bind_to_environ(request.environ)
      try:
         endpoint, values = adapter.match()
         return getattr(self, 'get_' + endpoint)(request, **values)
      except HTTPException, e:
         return e
