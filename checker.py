#!/usr/bin/env python

import re
from urlparse import urlparse
from urllib import unquote
from cgi import escape
import ipaddr, socket, httplib

URLINVALID = 0
URLV4LITERAL = 1
URLV6LITERAL = 2
URLHOSTNAME = 3

OWNHOSTNAMES = ['downforeveryoneorjustme', 'isup']

class UrlInvalidException(Exception):
    pass
class UrlSelfException(Exception):
    pass
class URLErrorException(Exception):
    pass

class CheckUrl(object):
  def get_hostname(self, url):
    # Unquote the URL to remove percent-encoding.
    url = unquote(url)
    # Parse the URL into a ParseResult object
    # urlparse gets confused with URLs that don't have a scheme specified, so first 
    # try with one added manually
    parsed_url = urlparse('http://' + url)
    # If that results in // at the start of the port number field then we shouldn't
    # have added http://, so try again without
    if parsed_url[2][:2] == '//':
      parsed_url = urlparse(url)
    # We only want to test http and only over port 80, so strip out port numbers to
    # leave us with just a hostname.  Also strip of the final . in case someone's 
    # being smart and including the root label.
    self.hostname = re.match(r'^(.*?)(\.|:\d+)?$', parsed_url.netloc, re.IGNORECASE).group(1).lower()
    try:
      # If the following succeeds then we have an ASCII hostname, which may be a 
      # plain ASCII hostname or a punycode encoded IDN
      self.display_url = escape('http://' + self.hostname.encode('ascii'))
      # If it's a punycode IDN then turn it into a unicode object for display later.
      if parsed_url.netloc.find('xn--') is not -1:
        self.display_url = escape(u'http://' + self.hostname.decode('idna'))
    except UnicodeDecodeError:
      # If the .encode('ascii') failed then we have a unicode hostname, so turn it 
      # into a unicode object for later display.
      self.display_url = escape(u'http://' + self.hostname.decode('utf-8'))
      # And we need the ASCII punycode equivalent for the actual testing.
      self.hostname = self.hostname.decode('utf-8').encode('idna')

  def validate_hostname(self):
    # Special message for people trying to implode the universe
    for hostname in OWNHOSTNAMES:
      if self.hostname.find(hostname) is not -1:
        raise UrlSelfException

  def understand_hostname(self):
    # IPv6 literals will begin with [
    if self.hostname[0] == '[':
      try:
        ip = ipaddr.IPAddress(self.hostname[1:-1], 6)
        self.hostname = self.hostname[1:-1]
        self.urltype = URLV6LITERAL
      except ValueError:
        # Anything else beginning with [ is invalid.
        raise UrlInvalidException
    # IPv4 literals are digits and .
    elif re.match(r'^[0-9\.]+$', self.hostname[-1]):
      try:
        ip = ipaddr.IPAddress(self.hostname, 4)
        self.urltype = URLV4LITERAL
      except ValueError:
        # Any other combination of [0-9\.]+ is invalid.
        raise UrlInvalidException
    # This should match normal ASCII domains.
    elif re.match(r'^[a-z0-9]+((\.|-|--)[a-z0-9]+)*$', self.hostname):
      self.urltype = URLHOSTNAME
    else:
      raise UrlInvalidException

  def http(self, ipaddr):
    try:
      h = httplib.HTTPConnection(ipaddr, 80, timeout=5)
      h.connect()
      h.putrequest('HEAD', '/', skip_host=True)
      h.putheader('Host', self.hostname)
      h.endheaders()
      r = h.getresponse()
      return r.status in [200,301,302,304]
    except:
      return False

  def ipv6_check(self):
    if self.urltype == URLV6LITERAL:
      self.up6 = self.http(self.hostname)
    elif self.urltype == URLHOSTNAME:
      try:
        self.up6 = self.http(socket.getaddrinfo(self.hostname, 'http', socket.AF_INET6)[0][4][0])
      except:
        pass

  def ipv4_check(self):
    if self.urltype == URLV4LITERAL:
      self.up4 = self.http(self.hostname)
    elif self.urltype == URLHOSTNAME:
      try:
        self.up4 = self.http(socket.getaddrinfo(self.hostname, 'http', socket.AF_INET)[0][4][0])
      except:
        pass

  def http_check(self, af='both'):
    if af != 'v4':
      self.ipv6_check()
    if af != 'v6':
      self.ipv4_check()

  def check(self, url, af='both'):
    self.success = False
    self.urltype = URLINVALID
    self.hostname = ''
    self.display_url = ''
    self.up4 = False
    self.up6 = False
    self.reason = 'error'
    try:
      self.get_hostname(url)
      self.validate_hostname()
      self.understand_hostname()
      self.http_check(af)
      self.success = True
      self.reason = 'valid'
    except UrlInvalidException:
      self.reason = 'invalid'
    except UrlSelfException:
      self.reason = 'hurr'
    except:
      pass

  def json(self):
    import json
    return json.dumps({
      'success': self.success,
      'urltype': self.urltype,
      'hostname': self.hostname,
      'up4': self.up4,
      'up6': self.up6,
      'reason': self.reason,
    })