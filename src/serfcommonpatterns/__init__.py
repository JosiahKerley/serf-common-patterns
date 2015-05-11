#!/usr/bin/python 

import os
import sys
import zlib
import stat
import time
import base64
import cPickle as pickle
from serfclient.client import SerfClient


## Settings
eventname = 'pattern'
lib = '/var/lib/serf-patterns'


class Serialize:
  def dumps(self,data):
    return(base64.b64encode(pickle.dumps(data)))
  def loads(self,data):
    return(pickle.loads(base64.b64decode(data)))


class Pipe:
  fifofiles = '/tmp/.serf-patterns.fifo/'
  def __init__(self):
    self.setup('default')
  def setup(self,name):
    fifofile = '%s/%s'%(self.fifofiles,name)
    if not stat.S_ISFIFO(os.stat(self.fifofile).st_mode):
      if os.path.isfile(self.fifofile):
        os.remove(self.fifofile)
      os.mkfifo(self.fifofile)
  def write(self,name,data):
    fifofile = '%s/%s'%(self.fifofiles,name)
    self.setup(name)
    with open(fifofile,'w') as f:
      f.write(data)
  def read(self,name):
    fifofile = '%s/%s'%(self.fifofiles,name)
    if stat.S_ISFIFO(os.stat(self.fifofile).st_mode):
      with open(fifofile,'r') as f:
        return(f)
    else:
      return(None)


class KeyValue:
  root = '%s/keyval'%(lib)
  namespace = 'keyval'
  client = SerfClient()
  serialize = Serialize()
  def __init__(self):
    if not os.path.isdir(self.root):
      os.makedirs(self.root)
  def set(self,key,value):
    self.client.event(eventname,self.serialize.dumps({"namespace":self.namespace,"command":"set","key":key,"value":value}))
    self.rx_set(key,value)
  def rx_set(self,key,value):
    keyfile = self.root+'/'+key
    with open(keyfile,'w') as f:
      f.write(self.serialize.dumps(value))
  def get(self,key,count=0):
    count += 1
    keyfile = self.root+'/'+key
    if os.path.isfile(keyfile):
      with open(keyfile,'r') as f:
        return(self.serialize.loads(f.read()))
    else:
      if count > 10:
        return(None)
      else:
        self.client.event(eventname,self.serialize.dumps({"namespace":self.namespace,"command":"rx_get","key":key}))
        return(self.get(key,count))
  def rx_get(self,key):
    keyfile = self.root+'/'+key
    if os.path.isfile(keyfile):
      with open(keyfile,'r') as f:
        value = self.serialize.loads(f.read())
        self.set(key,value)
  def delete(self,key):
    self.client.event(eventname,self.serialize.dumps({"namespace":self.namespace,"command":"delete","key":key}))
    self.rx_delete(key)
  def rx_delete(self,key):
    keyfile = self.root+'/'+key
    if os.path.isfile(keyfile):
      os.remove(keyfile)



class Queue:
  root = '%s/queue'%(lib)
  namespace = 'queue'
  client = SerfClient()
  serialize = Serialize()
  def __init__(self):
    if not os.path.isdir(self.root):
      os.makedirs(self.root)
  def push(self,name,data):
    self.client.event(eventname,self.serialize.dumps({"namespace":self.namespace,"command":"push","queue":name,"data":data}))
    self.rx_push(timestamp,key,value)
  def rx_push(self,timestamp,name,data):
    queuefolder = self.root+'/'+name
    queuefile = queuefolder+'/'+timestamp
    if not os.path.isdir(queuefolder):
      os.makedirs(queuefolder)
    with open(queuefile,'w') as f:
      f.write(self.serialize.dumps(value))
  def pop(self,name,select=0):
    queuefolder = self.root+'/'+name
    if os.path.isdir(queuefolder):
      self.client.event(eventname,self.serialize.dumps({"namespace":self.namespace,"command":"pop","queue":name,"file":files[select]}))
      files = os.listdir(queuefolder)
      queuefile = queuefolder+'/'+files[select]
      with open(queuefile,'r') as f:
        data = self.serialize.loads(f.read())
      self.rx_pop(name,files[select])
      return(data)
    else:
      return(None)
  def rx_pop(self,name,file):
    queuefolder = self.root+'/'+name
    queuefile = queuefolder+'/'+file
    if os.path.isfile(queuefile):
      os.remove(queuefile)
  def list(self,name):
    queuefolder = self.root+'/'+name
    files = os.listdir(queuefolder)
    items = []
    for i in files:
      queuefile = queuefolder+'/'+i
      with open(queuefile,'r') as f:
        data = self.serialize.loads(f.read())
      items.append(data)
    return(items)




class Handler:
  keyval = KeyValue()
  queue = Queue()
  serialize = Serialize()
  def __init__(self):
    payload = self.serialize.loads(sys.argv[-1])
    if payload['namespace'] == keyval.namespace:
      if payload['command'] == 'delete':
        keyval.rx_delete(payload['key'])
      elif payload['command'] == 'set':
        keyval.rx_set(payload['key'],payload['value'])
      elif payload['command'] == 'get':
        keyval.rx_get(payload['key'])
      else:
        raise('Unknown command "%s"'%(payload['command']))
    elif payload['namespace'] == queue.namespace:
      if payload['command'] == 'pop':
        queue.rx_pop(payload['queue'],payload['file'])
      elif payload['command'] == 'push':
        queue.rx_push(payload['queue'],payload['file'],payload['data'])
      else:
        raise('Unknown command "%s"'%(payload['command']))






