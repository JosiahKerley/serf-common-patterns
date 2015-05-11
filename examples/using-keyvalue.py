#!/usr/bin/python 
from serfcommonpatterns import KeyValue
kv = KeyValue()
print kv.get('foo')
kv.set('foo','bar')
print kv.get('foo')