import logging, unittest
from main import CheckUrlGAE

class CheckUrlTest(unittest.TestCase):
  def test_sane_url(self):
    cd = CheckUrlGAE()
    cd.result = {}
    cd.get_hostname('google.com')
    self.assertEqual('google.com', cd.hostname)
    
  def test_url_with_http(self):
    cd = CheckUrlGAE()
    cd.result = {}
    cd.get_hostname('http://google.com')
    self.assertEqual('google.com', cd.hostname)

  def test_url_with_http_encoded(self):
    cd = CheckUrlGAE()
    cd.result = {}
    cd.get_hostname('http%3A//google.com')
    self.assertEqual('google.com', cd.hostname)
