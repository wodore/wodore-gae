"""
License: MIT <http://brianmhunt.mit-license.org/>
"""
import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
sys.path.append('./')
sys.path.append('./model')

import logging
import unittest

from google.appengine.ext import ndb#, testbed


from counter import CountableLazy


class TestCountLazyModel(CountableLazy, ndb.Model):
  """This is a test class for trying out counters
  """
  name = ndb.StringProperty()

class TestCountLazyModelExtended(CountableLazy, ndb.Model):
  """This is a test class for trying out counters
  """
  name = ndb.StringProperty()
  toplevel = ndb.KeyProperty()
  collection = ndb.StringProperty(required=True, indexed=True,
                  default='global', validator=lambda p, v: v.lower())



class TestTags(unittest.TestCase):

  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    pass

  def tearDown(self):
    pass


  def test_init(self):
    tclm = TestCountLazyModel(name="X")
    tclm.put()
    assert tclm is not None
    self.assertEqual(tclm.count, 0)

  def test_counter_incr(self):
    tclm = TestCountLazyModel(name="X")
    tclm.incr()
    self.assertEqual(tclm.count, 1)
    tclm.incr(2)
    self.assertEqual(tclm.count, 3)
    tclm.put()
    self.assertEqual(tclm.count, 3)

  def test_counter_decr(self):
    tclm = TestCountLazyModel(name="X")
    tclm.decr()
    self.assertEqual(tclm.count, -1)
    tclm.decr(2)
    self.assertEqual(tclm.count, -3)
    tclm.put()

  def test_counter_saved(self):
    tclm = TestCountLazyModel(name="X")
    tclm.incr()
    key = tclm.put()
    self.assertEqual(str(key),"Key('TestCountLazyModel', 1)")
    tclm2 = key.get()
    self.assertEqual(tclm2.count, 1)

  def test_counter_incr_with_toplevel(self):
    top = TestCountLazyModelExtended(name="top")
    top_key = top.put()
    mid = TestCountLazyModelExtended(name="mid",
        toplevel = top_key,
        collection = 'mid')
    mid_key = mid.put()
    bot = TestCountLazyModelExtended(name="bot",
        toplevel = mid_key,
        collection = 'bot')
    bot_key = bot.put()
    self.assertEqual(top.count, 0)
    self.assertEqual(mid.count, 0)
    self.assertEqual(bot.count, 0)
    bot.incr()
    bot.put()
    self.assertEqual(top.count, 1)
    self.assertEqual(mid.count, 1)
    self.assertEqual(bot.count, 1)
    mid.incr()
    mid.put()
    self.assertEqual(top.count, 2)
    self.assertEqual(mid.count, 2)
    self.assertEqual(bot.count, 1)
    top.incr()
    top.put()
    self.assertEqual(top.count, 3)
    self.assertEqual(mid.count, 2)
    self.assertEqual(bot.count, 1)

#
#    def test_add_by_arg(self):
#        ttm = TestTagModel(name="X", tags=['a'])
#        ttm.put()
#        self.assertEqual(ttm.tags, ['a'])
#
#    def test_add_assign(self):
#        ttm = TestTagModel(name="X")
#        ttm.put()
#        ttm.tags = ['b']
#        self.assertEqual(ttm.tags, ['b'])
#
#    def test_del(self):
#        ttm = TestTagModel(name="X", tags=['b', 'c'])
#        ttm.put()
#        ttm.tags = ['c']  # delete 'b'
#        ttm.put()
#        b_tags = Tag.get_or_create_async('b').get_result()
#        c_tags = Tag.get_or_create_async('c').get_result()
#        self.assertEqual(len(b_tags.linked), 0)
#        self.assertEqual(len(c_tags.linked), 1)
#        self.assertEqual(len(b_tags.linked), b_tags.count)
#        self.assertEqual(len(c_tags.linked), c_tags.count)
#
#    def test_tag_count_none(self):
#        self.assertEqual(len(Tag.get_linked_by_tag('x')), 0)
#
#    def test_tag_count(self):
#        ttms = [
#            TestTagModel(name='X1', tags=['d']),
#            TestTagModel(name='X2', tags=['d']),
#            TestTagModel(name='X3', tags=['d']),
#        ]
#        for t in ttms:
#            t.put()
#        self.assertEqual(len(Tag.get_linked_by_tag('d')), 3)
#
#    def test_tag_count_del(self):
#        ttms = [
#            TestTagModel(name='X1', tags=['d']),
#            TestTagModel(name='X2', tags=['d']),
#            TestTagModel(name='X3', tags=['d']),
#        ]
#        for t in ttms:
#            t.put()
#        ttms[0].tags = []
#        ttms[0].put()
#        self.assertEqual(len(Tag.get_linked_by_tag('d')), 2)
#
#    def test_get_linked_by_tag(self):
#        TestTagModel(name='X1', tags=['a']).put()
#        TestTagModel(name='X2', tags=['b']).put()
#        TestTagModel(name='X3', tags=['b', 'c']).put()
#
#        self.assertEqual(len(Tag.get_linked_by_tag("a")), 1)
#        self.assertEqual(len(Tag.get_linked_by_tag("b")), 2)
#        self.assertEqual(len(Tag.get_linked_by_tag("zzz")), 0)
#
#    def test_popular_query(self):
#        TestTagModel(name='X1', tags=['a', 'b']).put()
#        TestTagModel(name='X2', tags=['b']).put()
#
#        res = Tag.get_popular_query().fetch(5)
#        self.assertEqual(len(res), 2)
#        self.assertEqual(res[0].tag, 'b')
#        self.assertEqual(res[1].tag, 'a')

if __name__ == "__main__":
    unittest.main()
