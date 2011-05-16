import unittest

from google.appengine.ext import webapp
from main import FrontPage, CheckUrlGAE
from webtest import TestApp

class MainTest(unittest.TestCase):
  def setUp(self):
    self.application = webapp.WSGIApplication([('/', FrontPage)], debug=True)

  def test_front_page(self):
    app = TestApp(self.application)
    response = app.get('/')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('down for everyone' in response)

class CheckUrlTest(unittest.TestCase):
  def setUp(self):
    self.application = webapp.WSGIApplication([(r'/(.*)', CheckUrlGAE)], debug=True)
    
  def test_page_with_param(self):
    app = TestApp(self.application)
    response = app.get('/google.com')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('google.com' in response)

  def test_known_bad_url(self):
    app = TestApp(self.application)
    response = app.get('/cse.ohio-state.edu')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('cse.ohio-state.edu' in response)
    self.assertTrue('down' in response)
    
  def test_amazon(self):
    app = TestApp(self.application)
    response = app.get('/amazon.com')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('amazon.com' in response)
    self.assertFalse('INVALID' in response)
    
  def test_google_with_http(self):
    app = TestApp(self.application)
    response = app.get('/http://google.com')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('google.com' in response)
    self.assertFalse('INVALID' in response)
    
  def test_idn(self):
    app = TestApp(self.application)
    response = app.get('/xn--mgbh0fb.xn--kgbechtv')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('xn--mgbh0fb.xn--kgbechtv'.decode('idna') in response)
    self.assertFalse('INVALID' in response)
    
  def test_idn_scheme(self):
    app = TestApp(self.application)
    response = app.get('/http://xn--mgbh0fb.xn--kgbechtv/')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('xn--mgbh0fb.xn--kgbechtv'.decode('idna') in response)
    self.assertFalse('INVALID' in response)
    
  def test_utf8(self):
    app = TestApp(self.application)
    response = app.get('/пример.испытание')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('пример.испытание' in response)
    self.assertFalse('INVALID' in response)
    
  def test_utf8_scheme(self):
    app = TestApp(self.application)
    response = app.get('/http://пример.испытание')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('http://пример.испытание' in response)
    self.assertFalse('INVALID' in response)

  def test_v4literal(self):
    app = TestApp(self.application)
    response = app.get('/http://1.2.3.4')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('http://1.2.3.4' in response)
    self.assertTrue('V4LITERAL' in response)

  def test_v4literal_port(self):
    app = TestApp(self.application)
    response = app.get('/http://1.2.3.4:234')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('http://1.2.3.4' in response)
    self.assertTrue('V4LITERAL' in response)

  def test_v6literal(self):
    app = TestApp(self.application)
    response = app.get('/[2a00:1450:400b:c00::63]')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('http://[2a00:1450:400b:c00::63]' in response)
    self.assertTrue('V6LITERAL' in response)

  def test_v6literal_port(self):
    app = TestApp(self.application)
    response = app.get('/[2a00:1450:400b:c00::63]:884')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('http://[2a00:1450:400b:c00::63]' in response)
    self.assertTrue('V6LITERAL' in response)

  def test_invalid(self):
    app = TestApp(self.application)
    response = app.get('/http://-------')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('INVALID' in response)

  def test__port(self):
    app = TestApp(self.application)
    response = app.get('/http://www.google.com:80')
    self.assertEqual('200 OK', response.status)
    self.assertTrue('VALID' in response)