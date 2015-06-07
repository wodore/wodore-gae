# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

# import do not work yet (for unit test)
# add them later
#import auth
from api import fields
import model
import util
import config

#from .tag import Taggable#, TagStructure, Tag, TagRelation
from .counter import CountableLazy


class Collection(CountableLazy, model.Base):
  """Collection model.

  This model saves all collections.
  The model CollectionUser saves all user which belong to a collection.
  The propertiy 'cnt' counts the user per collection.
  """
  name = ndb.StringProperty(required=True)
  description = ndb.TextProperty()
  active = ndb.BooleanProperty(required=True,default=True)
  public = ndb.BooleanProperty(required=True,default=False)
  creator = ndb.KeyProperty(kind="User") # default: current user key

  @classmethod
  def create(cls,name,creator,description=None,public=False,active=True,):
    """ Creates and puts a new collection to the database.
    The property creator is mandatory, it is best to given the current logged
    in user with: auth.current_user_key()

    Returns collection key
    """
    new_col = Collection(name=name,creator=creator,active=active, public=public)
    if description != None:
      new_col.description = description


    col_key =  new_col.put()
    cls.add_users(col_key,[creator],permission='creator')
    return col_key

  @classmethod
  def add_users(cls,collection_key,user_key_list,permission='read',active=True):
    """Add users to a collection.

    The default permission is 'read'.
    If the permission is different per user the user list needs to have the
    following form:
    user_key_list=[[key1,permission1],[key2,permission2],...]
    and persmission=False!

    This function can also be used to update a user (for example permission)
    """
    multi_permissions = not permission
    db_col = collection_key.get()
    for user_key in user_key_list:
      if multi_permissions:
        permission = user_key[1]
        user_key = user_key[0]
      user_db = user_key.get()
      if not user_db:
        continue
        # TODO create key with email (function in User)
      db, new = CollectionUser.get_or_create(CollectionUser.to_key_id(user_key), \
          parent=collection_key,user=user_key,collection=collection_key, \
          permission=permission, active=active, \
          user_name = user_db.name, user_username=user_db.username,\
          user_email=user_db.email, user_active=user_db.active,
          user_avatar_url = user_db.avatar_url)
      changed = False
      if not new: # make updates
        if db.permission != permission and db.permission != 'creator':
          # it is not possible to change the permission from creator to something else
          db.permission = permission
          changed = True
        if db.active != active:
          db.active = active
          changed = True
      if changed or new:
        db.put()
      if new:
        db_col.incr()

    db_col.put()

  @classmethod
  def remove_users(cls,collection_key,user_key_list):
    """Remove users from a collection.
    """
    db_col = collection_key.get()
    keys = []
    keys_checked = []
    for user_key in user_key_list:
      keys.append(CollectionUser.to_key(collection_key, user_key))
    dbs_to_check = ndb.get_multi(keys)
    for db in dbs_to_check:
      if db:
        keys_checked.append(db.key)
    deleted = ndb.delete_multi(keys_checked)
    db_col.decr(len(deleted))
    db_col.put()

  @classmethod
  def has_permission(cls,collection_key,user_key,permission='read', equal=False):
    """Checks if a user has a certain permission for a collection.

    Possible permissions are: 'creator', 'admin, 'write', 'read', 'none'.
    The permissions on the left include the one on the right as well.
    For example: 'admin' also has 'write' permission.
    If the flag equal=True then the permission must be equal ('admin' != 'write')
    """
    db_col = CollectionUser.to_key(collection_key, user_key).get()
    if not equal:
      return CollectionUser.permission_to_number(db_col.permission) >= \
         CollectionUser.permission_to_number(permission)
    else:
      return CollectionUser.permission_to_number(db_col.permission) == \
         CollectionUser.permission_to_number(permission)




  @classmethod
  def qry(cls, name=None, active=True, public='both', creator=None, \
      order_by_date='modified', **kwargs):
    """Query for collections, if active='both' it is not queried for active."""
    qry = cls.query(**kwargs)
    if name:
      qry_tmp = qry
      qry = qry.filter(cls.name==name)
    if creator:
      qry_tmp = qry
      qry = qry.filter(cls.creator==creator)
    if active == 'both':
      pass # nothing needed
    elif active:
      qry_tmp = qry
      qry = qry.filter(cls.active==True)
    elif not active:
      qry_tmp = qry
      qry = qry.filter(cls.active==False)
    if public == 'both':
      pass # nothing needed
    elif public:
      qry_tmp = qry
      qry = qry.filter(cls.public==True)
    elif not public:
      qry_tmp = qry
      qry = qry.filter(cls.public==False)
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
        +"-------------------+-------------------+-----------------------------+"
    print "| {:<18}| {:<18}| {:<18}| {:<18}| {:<18}| {:<28}|".\
        format("name", "description", "active","public","users", "creator", )
    print "+-------------------+-------------------+-------------------+"\
        +"-------------------+-------------------+-----------------------------+"
    for db in dbs:
      print "| {:<18}| {:<18}| {:<18}| {:<18}| {:<18}| {:<28}|".\
          format(db.name, db.description, db.active, db.public,db.count, db.creator)
    print "+-------------------+-------------------+-------------------+"\
        +"-------------------+-------------------+-----------------------------+"
    print
    print


  @classmethod
  def get_dbs(
      cls, name=None, active=None, creator=None,**kwargs
    ):
    return super(Collection, cls).get_dbs(
        name=name or util.param('name', None),
        active=active or util.param('active', bool),
        creator=creator or util.param('creator', ndb.Key),
        **kwargs
      )


  FIELDS = {
      'name' : fields.String,
      'active' : fields.Boolean,
      'creator' : fields.Key
    }

  FIELDS.update(model.Base.FIELDS)


class CollectionUser(model.Base):
  """Collection with User model.

  This model saves all users added to a collections.
  The collection key should be used as parent.
  """
  user = ndb.KeyProperty(kind="User",required=True) # default: current user key
  collection = ndb.KeyProperty(kind="Collection",required=True) # key to the collection,
                #should be the same as 'parent'
  active = ndb.BooleanProperty(required=True,default=True)
  permission = ndb.StringProperty(required=True,
      choices=['creator', 'admin','write','read','none'], default='read')
  user_name = ndb.StringProperty(required=True) # name property of User
  user_username = ndb.StringProperty(required=True) # username of User
  user_email = ndb.StringProperty(default='') # email of the user
  user_active = ndb.BooleanProperty(default=True) # is the user active
  user_avatar_url = ndb.StringProperty()

  @classmethod
  def update_user(cls, user_key):
    """Updates the user_* fields if a user changed"""
# TODO user a tasklet for this!!
# TODO add this to the user_update method in control/user.py
# TODO ad user_* to qry!
    user_db = user_key.get()
    if not user_db:
      return False
    # get all collections for this user
    dbs = []
    for db in cls.qry(user=user_key):
      db.user_name = user_db.name
      db.user_username = user_db.username
      db.user_email = user_db.email
      db.user_active = user_db.active
      if user_db.avatar_url:
        db.user_avatar_url = user_db.avatar_url
      dbs.append(db)
    ndb.put_multi(dbs)



  @staticmethod
  def permission_to_number(permission):
    """Returns a number for the permision"""
    perm_dic = {'none' : 0,
        'read' : 1,
        'write' : 2,
        'admin' : 3,
        'creator' : 5}
    return perm_dic[permission]

  @staticmethod
  def to_key_id(user_key):
    """Returns a key name (string)"""
    return "col_user__{}".format(user_key.urlsafe())

  @staticmethod
  def to_key(collection_key, user_key):
    """Returns a key"""
    return ndb.Key("CollectionUser", CollectionUser.to_key_id(user_key),\
        parent=collection_key)

  @classmethod
  def qry(cls, user=None, collection=None, active=True, permission=None, \
      user_email=None,
      order_by_date='modified', **kwargs):
    """Query for collections, if active='both' it is not queried for active."""
    qry = cls.query(**kwargs)
    if user:
      qry_tmp = qry
      qry = qry.filter(cls.user==user)
    if collection:
      qry_tmp = qry
      qry = qry.filter(cls.parent==collection)
    if active == 'both':
      pass # nothing needed
    elif active:
      qry_tmp = qry
      qry = qry.filter(cls.active==True)
    elif not active:
      qry_tmp = qry
      qry = qry.filter(cls.active==False)
    if permission:
      qry_tmp = qry
      qry = qry.filter(cls.permission==permission)
    if user_email:
      qry_tmp = qry
      qry = qry.filter(cls.user_email==user_email)
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
    print "\n+-----------------------------+-----------------------------+-------------------+"\
        +"-------------------+-------------------+-------------------+"
    print "| {:<28}| {:<28}| {:<18}| {:<18}| {:<18}| {:<18}|".\
        format("parent (collection)", "user", "active","permission","...", "...", )
    print "+-----------------------------+-----------------------------+-------------------+"\
        +"-------------------+-------------------+-------------------+"
    for db in dbs:
      print "| {:<28}| {:<28}| {:<18}| {:<18}| {:<18}| {:<18}|".\
          format(db.key.parent() or None, db.user_name, \
                db.active, db.permission,"","")
    print "+-----------------------------+-----------------------------+-------------------+"\
        +"-------------------+-------------------+-------------------+"
    print
    print

  FIELDS = { # parent key?
      'user' : fields.Key,
      'collection' : fields.Key,
      'active' : fields.Boolean,
      'permission' : fields.String
    }

  FIELDS.update(model.Base.FIELDS)




