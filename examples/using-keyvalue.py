#!/usr/bin/python 
from serfcommonpatterns import KeyVal
kv = KeyVal()
print kv.set('foo')
kv.set('foo','bar')
print kv.set('foo')