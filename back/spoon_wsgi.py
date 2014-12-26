import os
from service import SpoonerismService
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   currPath = os.path.dirname(__file__)
   template_path = os.path.join(currPath, '../front/templates')
   app = SpoonerismService(template_path)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/style':  os.path.join(currPath, '../front/style'),
   })
   return app