import sys, os
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
#sys.path.append('./')
#sys.path.append('./main')
sys.path.append('./model')


#import logging
import unittest

from google.appengine.ext import ndb#, testbed

from route import Route, RouteRefStructure, RouteDrawingStructure
from waypoint import WayPoint
from tag import TagStructure, Tag, TagRelation

class TestRoute(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True
  #import model # does not work yet

  def setUp(self):
    pass

  def test_init_route(self):
    R1 = Route(name='R1',collection='one')
    R1.put()
    assert R1 is not None
    self.assertEqual(R1.name, 'R1')
    self.assertEqual(R1.collection, 'one')

  def test_add_main_geo_coordinates_route(self):
    R1 = Route(name='R1',collection='one')
    R1.geo = ndb.GeoPt(52.37, 4.88)
    key = R1.put()
    R2 = key.get()
    self.assertEqual(R2.geo, ndb.GeoPt(52.37, 4.88))

  def test_route_tags(self):
    demo1 = Route(name='demo1',collection='one')
    demo1.add_tags(['one'])
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 2)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 0)

  def test_route_query(self):
    demo1 = Route(name='demo1',collection='one')
    demo1.add_tags(['one'])
    demo1.put()
    demo2 = Route(name='demo2',collection='one')
    demo2.add_tags(['one', 'two','three'])
    key2 = demo2.put()
    demo3 = Route(name='demo3',collection='one')
    demo3.add_tags(['two','three'])
    key3 = demo3.put()
    demo4 = Route(name='demo1',collection='two')
    demo4.add_tags(['three', 'four'])
    demo4.put()

    dbs = Route.qry(name='demo1').fetch()
    #Route.print_list(dbs)
    self.assertEqual(len(dbs), 2)
    self.assertEqual(dbs[0].name,'demo1')
    self.assertEqual(dbs[0].collection,'two')
    self.assertEqual(dbs[1].collection,'one')

    dbs = Route.qry(tag='three').fetch()
    #Route.print_list(dbs)
    self.assertEqual(len(dbs), 3)
    self.assertEqual(dbs[0].name,'demo1')
    self.assertEqual(dbs[0].collection,'two')

    dbs = Route.qry(collection='one').fetch()
    #Route.print_list(dbs)
    self.assertEqual(len(dbs), 3)

    demo2 = key2.get()
    demo2.update_tags(['three','two','one'])
    demo2.put()
    dbs = Route.qry(collection='one',tag='two',order_by_date='created').fetch()
    #Route.print_list(dbs)
    self.assertEqual(len(dbs), 2)
    self.assertEqual(dbs[0].name,'demo3')
    self.assertEqual(dbs[1].name,'demo2')
    dbs = Route.qry(collection='one',tag='two',order_by_date='modified').fetch()
    #Route.print_list(dbs)
    self.assertEqual(dbs[0].name,'demo2')
    self.assertEqual(dbs[1].name,'demo3')

  def test_route_ref_structure(self):
    demo1 = Route(name='demo1',collection='one')
    demo1.add_tags(['one'])
    wp1 = WayPoint(name='wp1',collection='one')
    wp1.add_tags(['one', 'two','three'])
    wp1_key = wp1.put()
    ref1 = RouteRefStructure(key=wp1_key,kind=wp1_key.kind())
    demo1.refs.append(ref1)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.name,'demo1')
    self.assertEqual(demo1t.refs[0],ref1)
# add the same again
    demo1.refs.append(ref1)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.refs[0],ref1)
    self.assertEqual(demo1t.refs[1],ref1)

  def test_route_add_ref_struct_same_collection(self):
    # Add ref strucuture wiht same collection
    demo1 = Route(name='demo1',collection='one')
    wp1 = WayPoint(name='wp1',collection='one')
    wp1_key = wp1.put()
    ref1 = RouteRefStructure(key=wp1_key,kind=wp1_key.kind())
    demo1.add_ref(ref1)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.name,'demo1')
    self.assertEqual(demo1t.refs[0],ref1)
    # and again
    demo1.add_ref(ref1)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.refs[1],ref1)

  def test_route_add_ref_struct_diff_collection(self):
    # Add ref strucuture wiht same collection
    demo1 = Route(name='demo1',collection='one')
    wp1 = WayPoint(name='wp1',collection='two')
    wp1_key = wp1.put()
    ref1 = RouteRefStructure(key=wp1_key,kind=wp1_key.kind())
    demo1.add_ref(ref1)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.refs[0].key.get().collection,'one')
    self.assertEqual(demo1t.refs[0].key.get().name,'wp1')

  def test_route_add_ref_key_same_collection(self):
    # Add ref strucuture wiht same collection
    demo1 = Route(name='demo1',collection='one')
    wp1 = WayPoint(name='wp1',collection='one')
    wp1_key = wp1.put()
    demo1.add_ref(ref_key=wp1_key)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.refs[0].key.get().collection,'one')
    self.assertEqual(demo1t.refs[0].key.get().name,'wp1')



if __name__ == "__main__":
  unittest.main()
