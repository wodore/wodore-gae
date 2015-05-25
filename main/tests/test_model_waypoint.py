import sys, os
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
#sys.path.append('./')
#sys.path.append('./main')
sys.path.append('./model')


#import logging
import unittest

from google.appengine.ext import ndb#, testbed

from waypoint import WayPoint
from tag import TagStructure, Tag, TagRelation

class TestWayPoint(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True
  #import model # does not work yet

  def setUp(self):
    pass

  def test_init_waypoint(self):
    P1 = WayPoint(name='P1',collection='one')
    P1.put()
    assert P1 is not None
    self.assertEqual(P1.name, 'P1')
    self.assertEqual(P1.collection, 'one')

  def test_add_geo_coordinates_waypoint(self):
    P1 = WayPoint(name='P1',collection='one')
    P1.geo = ndb.GeoPt(52.37, 4.88)
    key = P1.put()
    P2 = key.get()
    self.assertEqual(P2.geo, ndb.GeoPt(52.37, 4.88))


  def test_tags(self):
    demo1 = WayPoint(name='demo1',collection='one')
    demo1.add_tags(['one'])
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 2)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 0)
    #TagRelation.print_list(rel_dbs)

    demo1.add_tags(['two','three'])
    # show tags
    tag_dbs = Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 6)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 2*6)
    #TagRelation.print_list(rel_dbs)

    demo1.remove_tags(['two'])
    # show tags
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs), 4)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 2*2)
    #TagRelation.print_list(rel_dbs)

    demo1.update_tags(['two','three','four'])
    # show tags
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs), 6)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 2*6)
    #TagRelation.print_list(rel_dbs)




if __name__ == "__main__":
  unittest.main()
