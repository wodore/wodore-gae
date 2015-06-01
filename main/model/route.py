# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import geojson

# import do not work yet (for unit test)
# add them later
from api import fields
import model
import util
import config

#TODO import Taggable

#class WayPoint(model.Base): # does not work with unit test yet
from tag import Taggable#, TagStructure, Tag, TagRelation
#from waypoint import WayPoint#, TagStructure, Tag, TagRelation


class RouteRefStructure(ndb.Model): # use the counter mixin
  """Structure which helds the reference to either a waypoint or another route.
  The property kind must either be 'WayPoint' or 'Route'.
  A reference can be set to inactive, which leaves it in the route list but marked
  as inactive.
  """
  #tag_key = ndb.KeyProperty(required=False)
  active = ndb.BooleanProperty(required=True,default=True)
  key = ndb.KeyProperty() # reference, key to waypoint or another route
  kind = ndb.StringProperty(required=True,choices=['WayPoint','Route'])

class RouteDrawingStructure(ndb.Model): # use the counter mixin
  """Structure for further drawings on a route.
  The drawing is saved as GeoJSON.
  A drawing can be set to inactive, which leaves it in the route list but marked
  as inactive.
  """
  #tag_key = ndb.KeyProperty(required=False)
  name = ndb.StringProperty(required=True)
  drawing = ndb.JsonProperty(indexed=False) # GeoJSON Object (geojson)
  active = ndb.BooleanProperty(required=True,default=True)


class Route(Taggable, model.Base):
  """Route model.
  The properties are not very well defined yet.
  Not good is still visible, which should show if its includeds other routes or just waypoints).
  The property 'geo' shows a coordinate for the route, this might be the middle of all
  waypoints or a given point.
  """
  name = ndb.StringProperty(required=True)
  collection = ndb.StringProperty(required=True, indexed=True )
  visible = ndb.StringProperty(required=True,choices=['top','child','no'],default='top')
  description = ndb.TextProperty()
  refs = ndb.StructuredProperty(RouteRefStructure,repeated=True)
  drawings = ndb.StructuredProperty(RouteDrawingStructure,repeated=True)
  geo = ndb.GeoPtProperty(indexed=True) # lat/long coordinates of route (middle?)
  custom_fields = ndb.GenericProperty(repeated=True)
  creator = ndb.KeyProperty(kind="User") # default: current user key
  #created = ndb.DateTimeProperty(auto_now_add=True)
  #modified = ndb.DateTimeProperty(auto_now=True)

  def add_ref(self,ref_structure=None,ref_key=None,copy=True):
    """Add a reference strcuture, use this instead of directly add it to the property
    'refs'.
    If a ref_strcuture is given this is used, otherwise a ref_key needs to be added.
    The structure is then generated automatically.
    It is checked if the reference collection is the same as self.collection, if not
    the WayPoint or Route is copied (if copy=True) and then referenced.
    """
    if ref_structure:
      ref = ref_structure
    elif ref_key:
      ref = RouteRefStructure(key=ref_key,kind=ref_key.kind())
    else:
      raise UserWarning("At minimum the 'ref_key' parameter is needed.")

    # Check if it uses the same collection
    db = ref.key.get()
    if db.collection != self.collection and copy:
      new_db = self.__clone_entity(db,collection=self.collection)
      new_key = new_db.put()
      ref.key = new_key


    self.refs.append(ref)

  def add_drawing(self,drawing=None, drawing_geojson=None, name=None):
    """Either 'drawing' or 'drawing_geojson' is required.
    'drawing' is a `geojson` object. Preferable as 'Feature' or 'FeatureCollection'
    """
    if drawing_geojson:
      drawing = geojson.loads(drawing_geojson)
    if not name:
      name = "drawing {}".format(len(self.drawings)+1)

    draw_struct = RouteDrawingStructure(name=name,drawing=drawing)

    self.drawings.append(draw_struct)


  @classmethod
  def qry(cls, name=None, collection=None, tag=None, \
      order_by_date='modified', **kwargs):
    """Query for way points"""
    qry = cls.query(**kwargs)
    if name:
      qry_tmp = qry
      qry = qry.filter(cls.name==name)
    if collection:
      qry_tmp = qry
      qry = qry.filter(cls.collection==collection)
    if tag:
      qry_tmp = qry
      qry = qry.filter(cls.tags==tag)
    if order_by_date == 'modified':
      qry_tmp = qry
      qry = qry.order(-cls.modified)
    elif order_by_date == 'created':
      qry_tmp = qry
      qry = qry.order(-cls.created)
    #else filter for private True and False
    return qry

  @staticmethod
  def print_list(dbs):
    print "\n+-------------------+-------------------+-------------------+"\
        +"-------------------+-------------------+-----------------------"
    print "| {:<18}| {:<18}| {:<18}| {:<18}| {:<18}| {:<14} {:<48}".\
        format("name", "collection", "description", "ref", "geo", "tags", "custom field")
    print "+-------------------+-------------------+-------------------+"\
        +"-------------------+-------------------+-----------------------"
    for db in dbs:
      print "| {:<18}| {:<18}| {:<18}| {:<18}| {:<18}|{:<14} {:<48}".\
          format(db.name, db.collection, db.description, db.ref.key, db.geo,
          db.tags,db.custom_fields)
    print "+-------------------+-------------------+-------------------+"\
        +"-------------------+-------------------+-----------------------"
    print
    print


  def __clone_entity(self, e, **extra_args):
    klass = e.__class__
    props = dict((v._code_name, v.__get__(e, klass)) for v in \
        klass._properties.itervalues() if type(v) is not ndb.ComputedProperty)
    props.update(extra_args)
    return klass(**props)


  @classmethod
  def get_dbs(
      cls, name=None, collection=None, geo=None, creator=None, **kwargs
    ):
    return super(User, cls).get_dbs(
        name=name or util.param('name', None),
        collection=collection or util.param('collection', None),
        geo=geo or util.param('geo', None),
        creater=creater or util.param('creater', ndb.Key),
        **kwargs
      )


  FIELDS = {
    }

  FIELDS.update(model.Base.FIELDS)
