# coding: utf-8
from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model
import util
import config
from .counter import CountableLazy
from .collection import Collection, AddCollection

"""
An icon consists of two model classes:
  IconStructure: Which helds all icon specific data but no additional information.
  Icon: The Icon model contains an IconStructure as an icon and additional information
        like a counter and collection.

For each icon exists a toplevel icon which can have children grouped by collection.
Once an icon is created it should not be changed anymore.
If one of the childrens counter is updated the topevel icon's counter is updated
as well.
The highest toplevel has the default collection Collection.top_key().
"""


class IconStructure(ndb.Model): # use the counter mixin
  """Basic icon class
  """
  icon_key = ndb.KeyProperty(required=False)
  data = ndb.BlobProperty()
  external_source = ndb.StringProperty(indexed=False) # not recommended
  filetype = ndb.StringProperty(choices=['svg','png','external'],indexed=True,
                     default='svg', required=True)

class Icon(CountableLazy, AddCollection, model.Base):
  name = ndb.StringProperty(indexed=True,required=True)
  icon = ndb.StructuredProperty(IconStructure)
  private = ndb.BooleanProperty(required=True,default=False)
  replaced_by = ndb.KeyProperty() # if the icon should not be used anymore

  def get_icon(self):
    """ Returns a IconStructure.

    should be used instead of directly accessing the property 'icon'
    """
    if self.key is None:
      raise UserWarning("Key not set yet, use first 'put()' before you use this method.")
    self.icon.icon_key = self.key
    return self.icon

  @classmethod
  def create(cls,icon,name,collection=Collection.top_key()
      ,toplevel=None,private=False, auto=True):
    """ Creates and puts a new icon to the database.
    As icon is a IconStructure expected.
    Returns Icon key"""
    new_icon = Icon(icon = icon,
        name=name,
        collection=collection,
        private=private)
    if toplevel:
      new_icon.toplevel = toplevel

    key = new_icon._add_and_put(auto=auto)
    return key

  @classmethod
  def add(cls,key,collection=None, as_child=False):
    """ Add a icon which already exists by key.

    If no collection or the same belonging to the key is given the icon
    counter is increased by one.

    If the collection is different two things can happen:

    1. If the key's collection is Collection.top_key() (no toplevel) or 'as_child' is true:
       The key is assigned as toplevel.
       ('as_child' means the icon is added with key as toplevel)

    2. It is not a toplevel key:
       The property 'toplevel' is assigned as key.

    In both cases a toplevel is set. The next step is to look for a icon with
    the same toplevel and collection, if one exists its counter is increased.
    If none exists a new one is created.
      """
    icon_db = key.get()
    if icon_db.collection == collection or not collection:
      icon_db.incr()
      icon_db.put()
      return key
    else:
      if collection == Collection.top_key():
        return self.add(icon_db.toplevel,collection)
      elif icon_db.collection == Collection.top_key() or as_child:
        toplevel = key
      else:
        toplevel = icon_db.toplevel

    ## Look for icons with same toplevel and collection
    keys = Icon.get_by_toplevel(toplevel, collection=collection, keys_only=True, limit=1)
    if keys:
      #for key in keys:
      key = keys[0]
      return Icon.add(key,collection)
    else:
      return Icon.create(icon_db.icon,icon_db.name,collection=collection,toplevel=toplevel)

  @classmethod
  def remove(cls,key):
    """Removes a icon by its key

    Remove means its counter is decreased by one"""
    icon_db = key.get()
    icon_db.decr()
    icon_db.put()

  def get_tags(self,limit=10):
    """Fetches tags which are used together with this icon

    returns a tag dbs and a variable more if more tags are available."""
#TODO write test
    dbs = model.Tag.query(model.Tag.icon.icon_key==self.key)\
        .order(-model.Tag.cnt).fetch(limit+1)
    if len(dbs) > limit:
      more = True
    else:
      more = False
    return dbs, more



  @classmethod
  def qry(cls, toplevel=None, name=None, collection=None, private=False,
      replaced_by=None, order_by_count=True, **kwargs):
    """Query for the icon model"""
    qry = cls.query(**kwargs)
    if toplevel:
      qry_tmp = qry
      qry = qry.filter(cls.toplevel==toplevel)
    if name:
      qry_tmp = qry
      qry = qry.filter(cls.name==name,)
    if collection:
      qry_tmp = qry
      qry = qry.filter(cls.collection == collection)
    if not private:
      qry_tmp = qry
      qry = qry_tmp.filter(cls.private==False)
    if order_by_count:
      qry_tmp = qry
      qry = qry.order(-cls.cnt)
    #else filter for private True and False

    return qry

  @classmethod
  def get_by_toplevel(cls, toplevel=None, collection=None, private=False,
      keys_only=False, limit=100):
    """Returns icon dbs or keys defined by its toplevel and some addition parameters"""
    return cls.qry(toplevel=toplevel,collection=collection,private=private).\
        fetch(keys_only=keys_only, limit=limit)

  @classmethod
  def get_dbs(
      cls, name=None, private=None, \
          replaced_by=None, **kwargs
    ):
    kwargs = cls.get_col_dbs(**kwargs)
    kwargs = cls.get_counter_dbs(**kwargs)
    return super(Icon, cls).get_dbs(
        name=name or util.param('name', None),
        private=private or util.param('private', bool),
        replaced_by=replaced_by or util.param('replaced_by', ndb.Key),
        **kwargs
      )


  def _add_and_put(self, auto=True):
    """ Adds and puts an icon to the DB

    If 'auto' is true it automatically creates a toplevel icon if none is given.
    This only works for one level, if a higher hierarchy is required it needs to be
    done manually.
    """
    if not getattr(self,'toplevel',None) and self.collection != Collection.top_key() and auto: #\
      top = Icon(icon=self.icon,name=self.name)
      top_key = top.put()
      self.toplevel = top_key

    self.incr()
    self.put()
    self.get_icon()
    return self.key



class Iconize(ndb.Model): # use the counter mixin
  """Adds an icon property

  Icons are managed in the 'Icon' model, this mzixins
  adds two methods to deal with icons:
    'add_icon': if an icon already exists it can be added by its key
    'create_icon': create a new icon

  The two method 'put' the icons automatically, this means it is recommanded to
  put the iconized model as well or remove the icon again if something went wrong.
    """
  icon = ndb.StructuredProperty(IconStructure)

  def add_icon(self, key):
    """Adds an icon by key, the key is either a toplevel key or an icon key."""
    if not getattr(self,'collection',None):
      col = Collection.top_key()
    else:
      col = self.collection
    key = Icon.add(key,collection=col)
    self.icon = key.get().get_icon()

  def create_icon(self,icon,name,private=False):
    if not getattr(self,'collection',None):
      col = Collection.top_key()
    else:
      col = self.collection
    key = Icon.create(icon=icon,name=name,collection=col,private=private)
    icon.icon_key = key
    self.icon = icon

  def remove_icon(self):
    if getattr(self,'icon',None):
      Icon.remove(self.icon.icon_key)
      del self.icon

## TODO write test
  def get_icon_key(self):
    if getattr(self,'icon',None):
      return self.icon.icon_key
    elif getattr(self,'toplevel',None):
      top_db = self.toplevel.get()
      if getattr(top_db,'icon',None):
        return top_db.icon.icon_key
    else:
      None

