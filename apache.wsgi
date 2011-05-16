#!/usr/bin/env python

import sys, os
from cgi import parse_qs
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)
from checker import *

def application(environ, start_response):
  c = CheckUrl()
  try:
    c.check(parse_qs(environ.get('QUERY_STRING', ''))['url'][0],'v6')
  except:
    c.check('')
  output = c.json() 
  start_response(
    '200 OK',
    [
      ('Content-type', 'application/json'),
      ('Content-Length', str(len(output)))
    ]
    )
  return [output]