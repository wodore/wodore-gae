# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

# import do not work yet (for unit test)
# add them later
#from api import fields
#import model
#import util
#import config

#TODO import Taggable

#class WayPoint(model.Base): # does not work with unit test yet
from tag import Taggable#, TagStructure, Tag, TagRelation

class WayPoint(Taggable, ndb.Model):
  name = ndb.StringProperty(required=True)
  collection = ndb.StringProperty(required=True, indexed=True )
  description = ndb.TextProperty()
  url = ndb.StringProperty(validator=lambda p, v: v.lower())
  geo = ndb.GeoPtProperty(indexed=True) # lat/long coordinates
  custom_fields = ndb.GenericProperty(repeated=True)
  creator = ndb.KeyProperty(kind="User") # default: current user key
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)

  @classmethod
  def qry(cls, name=None, collection=None,  \
      url=None,  order_by_date='modified', **kwargs):
    """Query for way points"""
    qry = cls.query(**kwargs)
    if name:
      qry_tmp = qry
      qry = qry.filter(cls.name==name)
    if collection:
      qry_tmp = qry
      qry = qry.filter(cls.collection==collection)
    if url:
      qry_tmp = qry
      qry = qry.filter(cls.url==url.lower())
    if order_by_data == 'modified':
      qry_tmp = qry
      qry = qry.order(-cls.modified)
    elif order_by_data == 'created':
      qry_tmp = qry
      qry = qry.order(-cls.created)
    #else filter for private True and False
    return qry



# ADD them later
#  @classmethod
#  def get_dbs(
#      cls, admin=None, active=None, verified=None, permissions=None, **kwargs
#    ):
#    return super(User, cls).get_dbs(
#        admin=admin or util.param('admin', bool),
#        active=active or util.param('active', bool),
#        verified=verified or util.param('verified', bool),
#        permissions=permissions or util.param('permissions', list),
#        **kwargs
#      )
#
#
#  FIELDS = {
#    }
#
#  FIELDS.update(model.Base.FIELDS)
