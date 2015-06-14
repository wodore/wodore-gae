# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import config
import util


class Base(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)

  @classmethod
  def get_by(cls, name, value):
    return cls.query(getattr(cls, name) == value).get()

  @classmethod
  def get_dbs(cls, query=None, ancestor=None, order=None, limit=None, cursor=None, **kwargs):
    return util.get_dbs(
        query or cls.query(ancestor=ancestor),
        limit=limit or util.param('limit', int),
        cursor=cursor or util.param('cursor'),
        order=order or util.param('order'),
        **kwargs
      )

  @classmethod
  def id_to_key(cls,id_str):
    """ Returns key from a collection id """
    if id_str.isdigit():
      id = int(id_str)
    else:
      id = id_str
    return ndb.Key(cls._get_kind(),id)

  @classmethod
  @ndb.transactional
  def get_or_create(cls, id, parent=None, **kwargs):
    key = ndb.Key(cls, id, parent=parent)
    ent = key.get()
    if ent is not None:
      return (ent, False)  # False meaning "not created"
    ent = cls(**kwargs)
    ent.key = key
    ent.put()
    return (ent, True)  # True meaning "created"

  FIELDS = {
      'key': fields.Key,
      'id': fields.Id,
      'version': fields.Integer,
      'created': fields.DateTime,
      'modified': fields.DateTime,
    }
