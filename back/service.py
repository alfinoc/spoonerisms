from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest, Forbidden
from jinja2 import Environment, FileSystemLoader
from json import loads, dumps
from random import randint
from operator import add as concat
from passlib.apps import custom_app_context as pwd_context

from persistent import RedisStore

HASH_FILE = 'pass.hash'

class SpoonerismService(object):

   def get_random(self, request):
      enabled = self.store.getEnabledList()
      index = randint(0, len(enabled) - 1)
      spoon = enabled[index]
      return self.render('random.html', index=index + 1, spoon=spoon,
                         ext='random')

   def get_archive(self, request):
      enabled = self.store.getEnabledList()
      return self.render('archive.html', spoons=enabled, ext='archive')

   def get_submit(self, request):
      return self.render('submit.html', ext='submit')

   def get_accept(self, request, ext='accept'):
      try:
         spoon = request.args['spoon']
         self.store.addSpoon(spoon)
      except:
         return self.render('taco.html', ext='accept')
      return self.render('accept.html', ext='accept')

   def get_screen(self, request, ext='screen'):
      full = self.store.getFullList();
      enabled = self.store.getEnabledList()
      full = map(lambda s : {'spoon': s, 'enabled': s in enabled}, full)
      return self.render('screen.html', spoons=full, ext='screen')

   def get_modified(self, request, ext='modified'):
      submission = ''
      if 'password' in request.form:
         submission = request.form['password']
      if not pwd_context.verify(submission, self.password):
         return Forbidden('Wrong password.')
      prev = set(self.store.getEnabledList())
      new = set(request.form.keys()) - set(['password'])
      whitelist = new - prev
      blacklist = prev - new
      delta = set()
      for s in blacklist:
         self.store.disable(s)
      for s in whitelist:
         self.store.enable(s)
      return self.render('modified.html', modded=whitelist.union(blacklist),
                         ext='modified')

   """
   dispatch requests to appropriate functions above
   """
   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/', endpoint='random'),
         Rule('/archive', endpoint='archive'),
         Rule('/submit', endpoint='submit'),
         Rule('/accept', endpoint='accept'),
         Rule('/screen', endpoint='screen'),
         Rule('/modified', endpoint='modified'),
         Rule('/<all>', redirect_to=''),
      ])
      self.password = reduce(concat, open(HASH_FILE)).strip()
      self.store = RedisStore()
      self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                   autoescape=True)

   def render(self, template_name, **context):
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
