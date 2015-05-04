# coding: utf-8

from __future__ import absolute_import
import unittest
import sys
sys.path.append('/home/tobias/data/git/wodore-gae/main/')
print sys.path
print "Hallo Test"

#import model
from model import tags


# Ignore UserWarnings cause by jinja2 using pkg_resources.py
#warnings.simplefilter('ignore')


class test_tag(unittest.TestCase):

  def setUp(self):
    #from main.model.tags import *
    pass

  def test_add_tagname(self):
    #assert True == False
    assert True == True
    #first = Tag('first')
    #assert first.get_name == 'first'


#if __name__ == '__main__':
    #unittest.main()
