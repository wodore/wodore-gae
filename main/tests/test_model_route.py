import sys, os
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
#sys.path.append('./')
#sys.path.append('./main')
#sys.path.append('./model')


#import logging
import unittest

from google.appengine.ext import ndb#, testbed

import geojson as gj

#from route import Route, RouteRefStructure, RouteDrawingStructure
#from waypoint import WayPoint
#from tag import TagStructure, Tag, TagRelation

class TestRoute(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True
  #import model # does not work yet

  def setUp(self):
    global config
    global model
    import config
    import model
    self.col1 = ndb.Key('Collection','one')
    self.col2 = ndb.Key('Collection','two')

  def test_init_route(self):
    R1 = model.Route(name='R1',collection=self.col1)
    R1.put()
    assert R1 is not None
    self.assertEqual(R1.name, 'R1')
    self.assertEqual(R1.collection, self.col1)

  def test_add_main_geo_coordinates_route(self):
    R1 = model.Route(name='R1',collection=self.col1)
    R1.geo = ndb.GeoPt(52.37, 4.88)
    key = R1.put()
    R2 = key.get()
    self.assertEqual(R2.geo, ndb.GeoPt(52.37, 4.88))

  def test_route_tags(self):
    demo1 = model.Route(name='demo1',collection=self.col1)
    demo1.add_tags(['one'])
    demo1.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 2)
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 0)

  def test_route_query(self):
    demo1 = model.Route(name='demo1',collection=self.col1)
    demo1.add_tags(['one'])
    demo1.put()
    demo2 = model.Route(name='demo2',collection=self.col1)
    demo2.add_tags(['one', 'two','three'])
    key2 = demo2.put()
    demo3 = model.Route(name='demo3',collection=self.col1)
    demo3.add_tags(['two','three'])
    key3 = demo3.put()
    demo4 = model.Route(name='demo1',collection=self.col2)
    demo4.add_tags(['three', 'four'])
    demo4.put()

    dbs = model.Route.qry(name='demo1').fetch()
    #model.Route.print_list(dbs)
    self.assertEqual(len(dbs), 2)
    self.assertEqual(dbs[0].name,'demo1')
    self.assertEqual(dbs[0].collection,self.col2)
    self.assertEqual(dbs[1].collection,self.col1)

    dbs = model.Route.qry(tag='three').fetch()
    #model.Route.print_list(dbs)
    self.assertEqual(len(dbs), 3)
    self.assertEqual(dbs[0].name,'demo1')
    self.assertEqual(dbs[0].collection,self.col2)

    dbs = model.Route.qry(collection=self.col1).fetch()
    #model.Route.print_list(dbs)
    self.assertEqual(len(dbs), 3)

    demo2 = key2.get()
    demo2.update_tags(['three','two','one'])
    demo2.put()
    dbs = model.Route.qry(collection=self.col1,tag='two',order_by_date='created').fetch()
    #model.Route.print_list(dbs)
    self.assertEqual(len(dbs), 2)
    self.assertEqual(dbs[0].name,'demo3')
    self.assertEqual(dbs[1].name,'demo2')
    dbs = model.Route.qry(collection=self.col1,tag='two',order_by_date='modified').fetch()
    #model.Route.print_list(dbs)
    self.assertEqual(dbs[0].name,'demo2')
    self.assertEqual(dbs[1].name,'demo3')

  def test_route_ref_structure(self):
    demo1 = model.Route(name='demo1',collection=self.col1)
    demo1.add_tags(['one'])
    wp1 = model.WayPoint(name='wp1',collection=self.col1)
    wp1.add_tags(['one', 'two','three'])
    wp1_key = wp1.put()
    ref1 = model.RouteRefStructure(key=wp1_key,kind=wp1_key.kind())
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
    demo1 = model.Route(name='demo1',collection=self.col1)
    wp1 = model.WayPoint(name='wp1',collection=self.col1)
    wp1_key = wp1.put()
    ref1 = model.RouteRefStructure(key=wp1_key,kind=wp1_key.kind())
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
    demo1 = model.Route(name='demo1',collection=self.col1)
    wp1 = model.WayPoint(name='wp1',collection=self.col2)
    wp1_key = wp1.put()
    ref1 = model.RouteRefStructure(key=wp1_key,kind=wp1_key.kind())
    demo1.add_ref(ref1)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.refs[0].key.get().collection,self.col1)
    self.assertEqual(demo1t.refs[0].key.get().name,'wp1')

  def test_route_add_ref_key_same_collection(self):
    # Add ref strucuture wiht same collection
    demo1 = model.Route(name='demo1',collection=self.col1)
    wp1 = model.WayPoint(name='wp1',collection=self.col1)
    wp1_key = wp1.put()
    demo1.add_ref(ref_key=wp1_key)
    demo1_key = demo1.put()
    demo1t = demo1_key.get()
    self.assertEqual(demo1t.refs[0].key.get().collection,self.col1)
    self.assertEqual(demo1t.refs[0].key.get().name,'wp1')

  def test_route_add_drawing(self):
    my_point = gj.Point((-3.68, 40.41))
    drawing = gj.Feature(geometry=my_point, properties={"country": "Spain"})
    demo1 = model.Route(name='demo1',collection=self.col1)
    demo1.add_drawing(drawing=drawing)
    self.assertEqual(demo1.drawings[0].name,'drawing 1')
    self.assertEqual(demo1.drawings[0].drawing,drawing)
# another drawing
    my_point2 = gj.Point((-5.68, 42.41))
    drawing = gj.Feature(geometry=my_point2, properties={"country": "Portugal"})
    demo1.add_drawing(drawing=drawing)
    self.assertEqual(demo1.drawings[1].name,'drawing 2')
    self.assertEqual(demo1.drawings[1].drawing,drawing)
# add one as GeoJSON
    my_point3 = gj.Point((-7.68, 44.41))
    drawing = gj.Feature(geometry=my_point3, properties={"country": "Chinese"})
    demo1.add_drawing(drawing_geojson=gj.dumps(drawing), name='DRAW3')
    self.assertEqual(demo1.drawings[2].name,'DRAW3')
    self.assertEqual("".format(demo1.drawings[2].drawing),"".format(drawing))
# add one as GeoJSON





if __name__ == "__main__":
  unittest.main()
