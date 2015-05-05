# coding: utf-8

#from __future__ import absolute_import
import unittest
import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
sys.path.append('./')

#import model
import model_app as mod

#print dir()
# Ignore UserWarnings cause by jinja2 using pkg_resources.py
#warnings.simplefilter('ignore')


class test_tag(unittest.TestCase):

  def setUp(self):
    #from main.model.tags import *
    pass

  def test_basic_tag_functions(self):
    tag_one = mod.Tag('tag one')
    self.assertEqual(tag_one.name,'tag one')
    tag_one.rename('Another name')
    self.assertEqual(tag_one.name,'Another name')
    # by default the counter should be 0 (if not added yet)
    self.assertEqual(tag_one.counter,0)
    tag_one.add() # counter increases
    self.assertEqual(tag_one.counter,1)
    tag_one.remove()
    self.assertEqual(tag_one.counter,0)

  def test_non_string_inputs(self):
    tag_wrong = mod.Tag(1) # integer instead of string
    self.assertTrue(isinstance(tag_wrong.name,basestring))
    test_array = ['one','two','three']
    tag_wrong = mod.Tag(test_array) # array instead of sring
    self.assertEqual(tag_wrong.name,str(test_array))

  def test_remove_too_much(self):
    tag_one = mod.Tag('tag one')
    tag_one.remove()
    self.assertEqual(tag_one.counter,0)
    tag_one.remove()
    self.assertEqual(tag_one.counter,0)
    tag_one.add() # counter increases
    self.assertEqual(tag_one.counter,1)

  def test_new_tag_without_name(self):
    with self.assertRaises(TypeError):
      tag_empty = mod.Tag()

  def test_set_tag_name(self):
    tag_one = mod.Tag('tag one')
    with self.assertRaises(AttributeError):
      tag_one.name = 'New name'




#if __name__ == '__main__':
    #unittest.main()

