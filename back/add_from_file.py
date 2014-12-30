from datetime import datetime
from persistent import RedisStore, DATE_FORMAT

def lineToPackage(line):
   parts = line.split('|')
   parts = map(lambda tok : tok.strip(), parts)
   parts = filter(lambda tok : tok != '', parts)
   # i and j are junk (id and rating?)
   i, spoon, j, date, enabled = parts
   return { 'spoon': spoon, 'date': date, 'enabled': enabled == '1' }

def parseDate(s):
   return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

f = open('data/raw.txt')
lines = []
spoons = map(lineToPackage, f)
store = RedisStore()
for s in spoons:
   store.addSpoon(s['spoon'], s['enabled'], parseDate(s['date']))
store.store.save()