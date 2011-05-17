#!/usr/bin/env python

import os, wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.api import urlfetch

try:
  from google.appengine.runtime import DeadlineExceededError
except ImportError:
  from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

from checker import *

class FrontPage(webapp.RequestHandler):
  def get(self):
    return self.response.out.write(
      template.render(
        os.path.join(os.path.dirname(__file__), 'templates', 'home.html'),
        {},
        )
      )

class CheckUrlGAE(webapp.RequestHandler, CheckUrl):
  def render(self, why='error'):
    return self.response.out.write(
      template.render(
        os.path.join(os.path.dirname(__file__), 'templates', why+'.html'),
        {
          'display_url': self.display_url,
          'up4': self.up4,
          'up6': self.up6,
          'upad1': '<div class="ad"><p>We Guarantee Our Uptime! Switch to <a href="http://gk.site5.com/t/83/1" class="adlink">Site5 Web Hosting</a>!</p></div>',
          'downad1': '<div class="ad"><p>Tired Of Downtime? Switch to <a href="http://gk.site5.com/t/83/2" class="adlink">Site5 Web Hosting</a>!</p></div>',
        },
        )
      )

  def validate_hostname(self):
    # Special message for people trying to implode the universe
    for hostname in OWNHOSTNAMES:
      if self.hostname.find(hostname) is not -1:
        raise UrlSelfException
    # Limit tests to 500 per minute per host.
    if memcache.get(self.hostname) is None:
      if not memcache.add(self.hostname, 0, 60):
        raise URLErrorException
    if memcache.incr(self.hostname, initial_value=0) > 500:
      raise URLErrorException

  def http_check(self, af='both'):
    if self.urltype != URLV6LITERAL:
      # Test over IPv4
      self.rpc_ipv4 = urlfetch.create_rpc()
      urlfetch.make_fetch_call(self.rpc_ipv4, 'http://'+self.hostname, method=urlfetch.HEAD, follow_redirects=False)
    if self.urltype != URLV4LITERAL:
      # Test over IPv6
      self.rpc_ipv6 = urlfetch.create_rpc()
      if self.urltype == URLV6LITERAL:
        urlfetch.make_fetch_call(self.rpc_ipv6, 'http://isupme.psimonkey.org.uk/?url=['+self.hostname+']', method=urlfetch.GET, follow_redirects=False)
      else:
        urlfetch.make_fetch_call(self.rpc_ipv6, 'http://isupme.psimonkey.org.uk/?url='+self.hostname, method=urlfetch.GET, follow_redirects=False)
    if self.urltype != URLV6LITERAL:
      try:
        response = self.rpc_ipv4.get_result()
        if response.status_code in [200,301,302,304]:
          self.up4 = True
      except (urlfetch.Error, DeadlineExceededError):
        pass
    if self.urltype != URLV4LITERAL:
      try:
        import simplejson as json
        response = json.loads(self.rpc_ipv6.get_result().content)
        self.up6 = response[u'up6']
      except (urlfetch.Error, DeadlineExceededError):
        pass
      pass
  
  def get(self, url):
    self.check(self.request.get('url', url))
    if self.success:
      if self.urltype == URLV6LITERAL:
        return self.render('v6literal')
      elif self.urltype == URLV4LITERAL:
        return self.render('v4literal')
    return self.render(self.reason)

def main():
  application = webapp.WSGIApplication([('/', FrontPage),
                                        (r'/(.*)', CheckUrlGAE)],
                                       debug=False)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
