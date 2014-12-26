import redis
from datetime import datetime

HOST = 'localhost'
PORT = '6379'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

"""
Key scheme:
   list -> list<<spoon>>
   enabled -> set<<spoon>>
   <spoon>:date -> <date>
"""
class RedisStore:
   def __init__(self):
      try:
         self.store = redis.Redis(HOST, port=PORT)
      except redis.ConnectionError:
         raise IOError

   def getFullList(self):
      return self.store.lrange('list', 0, -1)

   def getEnabledList(self):
      enabled = self.store.smembers('enabled')
      return filter(lambda s : s in enabled, self.getFullList())

   def addSpoon(self, spoon, enabled=False, date=datetime.now()):
      if self.store.exists(spoon):
         raise ValueError('Existing entry for %s.' % spoon)

      self.store.rpush('list', spoon)
      if enabled:
         self.enable(spoon)
      self.setDate(spoon, date)

   def setDate(self, spoon, date):
      self.store.set(spoon + ':date', date.strftime(DATE_FORMAT))

   def getDate(self, spoon):
      return datetime.strptime(self.store.get(spoon + ':date'), DATE_FORMAT) 

   def enable(self, spoon):
      self.store.sadd('enabled', spoon)

   def disable(self, spoon):
      self.store.srem('enabled', spoon)

   def isEnabled(self, spoon):
      return self.sismember(spoon)
