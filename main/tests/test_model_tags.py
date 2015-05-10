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


from tags import _Tag, _TagCount, _IconStructure, _TagIcon, Taggable


class TestTagModel(Taggable, ndb.Model):
    """This is a test class for trying out tags
    """
    name = ndb.StringProperty()


class TestTags(unittest.TestCase):

    # enable the datastore stub
    nosegae_datastore_v3 = True
    nosegae_memcache = True

    def setUp(self):
      pass

    def tearDown(self):
      pass


    def test_init(self):
        ttm = TestTagModel(name="X")
        ttm.put()
        assert ttm is not None
        self.assertEqual(ttm.tags, [])
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
