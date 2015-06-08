# coding: utf-8
from __future__ import absolute_import
from google.appengine.ext import ndb

from api import fields
import model
import util
import config

from .counter import CountableLazy
from .icon import IconStructure, Iconize

"""
A tag consists of three model classes:
  TagStructure: Which holds all tag specific data but no additional information.
  Tag: The 'Tag' model contains additional information for a tag like a counter
       and collection. A 'TagStructure' is return by 'get_tag()'.
  TagRelation: Which saves relations between tags.

For each tag exists a toplevel tag which can have children grouped by a collection.
Once a tag is created it should not be changed anymore.
If one of the children's counter is updated the topevel tag counter is updated
as well.
The highest toplevel has the default collection 'global'.
A tag key look as follow : 'tag__{name}_{collection}'.
"""


class TagStructure(ndb.Model): # use the counter mixin
  """Basic tag class
  """
  #tag_key = ndb.KeyProperty(required=False)
  icon = ndb.StructuredProperty(IconStructure)
  name = ndb.StringProperty(indexed=True,required=True)
  color = ndb.StringProperty(indexed=True,required=True)

class Tag(Iconize, CountableLazy, model.Base):
  """Tag Model
  The key should have the following from: tag__{name}_{collection}"""
  name = ndb.StringProperty(indexed=True,required=True, validator=lambda p, v: v.lower())
  color = ndb.StringProperty(indexed=True,required=True,default='blue')
  approved = ndb.BooleanProperty(required=True,default=False)
  #created = ndb.DateTimeProperty(auto_now_add=True)
  #modified = ndb.DateTimeProperty(auto_now=True)
  # Preferred urlsafe keys
  collection = ndb.StringProperty(required=True, indexed=True,
                  default='global')#, validator=lambda p, v: v.lower())
  # Key to the parent (or toplevel) entry. If empty it is already the toplevel,
  # usually the collection 'global'
  toplevel = ndb.KeyProperty()
  #replaced_by = ndb.KeyProperty() # if the icon should not be used anymore

  def get_tag(self):
    """ Returns a TagStructure.

    Should be used instead of directly accessing the properties for a tag.
    This can be saved as a property be other models.
    """
    #if self.key is None:
      #raise UserWarning("Key not set yet, use first 'put()' before you use this method.")
    #self.icon.icon_key = self.key
    return TagStructure(name=self.name,icon=getattr(self,'icon',None) \
        ,color=self.color)

  def related(self,limit=5):
    dbs, _ = model.TagRelation.get_dbs(tag_name=self.name,\
        collection=self.collection,limit=limit+1,\
        order='-cnt')
    if len(dbs) > limit:
      more = True
    else:
      more = False
    return dbs[:-2], more

  @staticmethod
  def tag_to_keyname(name,collection=None):
    """Returns a key name (string)"""
    col = collection or 'global'
    return "tag__{}_{}".format(name.lower(), col)

  @staticmethod
  def tag_to_key(name, collection=None):
    """Returns a key"""
    return ndb.Key("Tag", Tag.tag_to_keyname(name,collection))

  @staticmethod
  def tag_structures_to_tagnames(tag_structures):
    tagnames = []
    for tag in tag_structures:
      tagnames.append(tag.name)
    return tagnames

  @classmethod
  def add(cls,name,collection=None, toplevel_key=None, icon_key=None, \
      icon_structure=None, color=None, force_new_icon=False, auto_incr=True):
    """ Add a tag, if it not exists create one.

    If an 'icon_strucuture' is given a new icon is created for the icon DB,
    if an 'icon_key' is given this icon is used.

    An icon can only be added once, except 'force_new_icon' is 'True'
    This method already 'put()'s the tag to the DB.
      """
    col = collection or 'global'
    #key = ndb.Key('Tag','tag_{}_{}'.format(name,col))
    #print key
    tag_db = Tag.get_or_insert(Tag.tag_to_keyname(name,col),\
        name=name.lower(),collection=col)
    if col != 'global' and not toplevel_key:
      tag_db.toplevel = Tag.tag_to_key(name,'global')
      top_db = Tag.get_or_insert(Tag.tag_to_keyname(name,'global'),\
        name=name.lower(),collection='global')
      top_db.put()
    elif toplevel_key:
      tag_db.toplevel = toplevel_key
    if auto_incr:
      tag_db.incr()
    # check if icon already exists
    if not tag_db.get_tag().icon or force_new_icon:
      if icon_key:
        tag_db.add_icon(icon_key)
      elif icon_structure:
        tag_db.create_icon(icon_structure,name)
    if color:
      tag_db.color = color
    return tag_db.put()

  @classmethod
  def remove(cls,name,collection=None):
    """Removes a tag by its name"""
# TODO Should it also work with a key??
    col = collection or 'global'
    tag_db = Tag.tag_to_key(name,col).get()
    if tag_db:
      tag_db.decr()
      if tag_db.get_tag().icon:
        tag_db.remove_icon()
      return tag_db.put()
    else:
      return False

  @classmethod
  def approve(cls,name,collection=None,approved=True):
    """The method approves a tag, by default only global tags need improvement"""
    col = collection or 'global'
    tag_db = Tag.tag_to_key(name,col).get()
    tag_db.approved=approved
    return tag_db.put()


  @classmethod
  def qry(cls, toplevel=None, name=None, collection=None, only_approved=False,
      order_by_count=True, count_greater=0, **kwargs):
    """Query for the icon model"""
    qry = cls.query(cls.cnt > count_greater, **kwargs)
    if toplevel:
      qry_tmp = qry
      qry = qry.filter(cls.toplevel==toplevel)
    if name:
      qry_tmp = qry
      qry = qry.filter(cls.name==name.lower())
    if collection:
      qry_tmp = qry
      qry = qry.filter(cls.collection == collection)
    if only_approved:
      qry_tmp = qry
      qry = qry_tmp.filter(cls.approved==True)
    if order_by_count:
      qry_tmp = qry
      qry = qry.order(-cls.cnt)
    #else filter for private True and False
    return qry

  @classmethod
  def get_dbs(
      cls, name=None, color=None, approved=None, collection=None,
      toplevel=None, **kwargs
    ):
    return super(Tag, cls).get_dbs(
        name=name or util.param('name', str),
        color=color or util.param('color', str),
        approved=approved or util.param('approved', bool),
        collection=collection or util.param('collection', str),
        toplevel=toplevel or util.param('toplevel', ndb.Key),
        **kwargs
      )


  @staticmethod
  def print_list(dbs):
    print "\n+-------------------+-------------------+-------------------"\
        +"+-------------------+-----------+-------------------+"\
        +"---------------------------------------+"
    print "| {:<18}| {:<18}| {:<18}| {:<18}| {:<10}| {:<18}| {:<38}|".\
        format("name", "collection", "icon", "color", \
        "count", "approved", "toplevel")
    print "+-------------------+-------------------+-------------------"\
        +"+-------------------+-----------+-------------------+---------------------------------------+"
    for db in dbs:
      print "| {:<18}| {:<18}| {:<18}| {:<18}| {:<10}| {:<18}| {:<38}|".\
          format(db.name, db.collection, \
          getattr(db.icon,"icon_key",""), db.color, db.count, db.approved, db.toplevel or "")
    print "+-------------------+-------------------+-------------------"\
        +"+-------------------+-----------+-------------------+"\
        +"---------------------------------------+"
    print
    print

class TagRelation(CountableLazy, model.Base): # use the counter mixin
  """Tag relation model
  Saves all relation between tags with a counter.
  Can be used for tag suggestions.

  key: tagrel__{tag_name}_{relate_to}_{collection}
  """
  tag_name = ndb.StringProperty(indexed=True,required=True)
  related_to = ndb.StringProperty(indexed=True,required=True)
  collection = ndb.StringProperty(indexed=True,required=True,default='global')
  toplevel = ndb.KeyProperty()
  #created = ndb.DateTimeProperty(auto_now_add=True)
  #modified = ndb.DateTimeProperty(auto_now=True)

  @staticmethod
  def to_keyname(tag_name,related_to,collection=None):
    """Returns a key name (string)"""
    col = collection or 'global'
    return "tagrel__{}_{}_{}".format(tag_name.lower(),related_to.lower(), col)

  @staticmethod
  def from_keyname(keyname):
    """Returns tag_name, related_to, collection """
    names = keyname.split('_')
    tag_name = names[2]
    related_to = names[3]
    collection = names[4]
    return tag_name, related_to, collection

  @classmethod
  def from_key(cls,key):
    """Returns tag_name, related_to, collection """
    return cls.from_keyname(key.id())


  @classmethod
  def to_key(cls, tag_name, related_to, collection=None):
    """Returns a key"""
    return ndb.Key("TagRelation", cls.to_keyname(tag_name,related_to,collection))


  @classmethod
  def generate_all_keys(cls, tag_names, collection=None):
    """Generates all key combination depending on a tag name list"""
    keys = []
    for tag_name in tag_names:
      keys.extend(cls.generate_related_keys(tag_name,tag_names,collection))
    return keys

  @classmethod
  def generate_related_keys(cls,tag_name,related_tos,collection=None):
    """Generates all keys from one tag name to a list of related tags"""
    keys = []
    for related_to in related_tos:
      if related_to != tag_name:
        keys.append(cls.to_key(tag_name,related_to,collection))
    return keys

  @classmethod
  def add_by_keys(cls,tag_rel_keys,_incr_step=1):
    """Add relation by keys

    Toplevels are added automatically."""
    keys = tag_rel_keys
    dbs = ndb.get_multi(keys)
    dbs_new = []
    keys_del = []
    for db, key in zip(dbs, keys):
      if not db:
        tag_name, related_to, collection = cls.from_key(key)
        db = cls.get_or_insert(key.id(),tag_name=tag_name,related_to=related_to,\
            collection=collection,cnt=0)
        if collection != 'global':
          top_key = cls.to_key(tag_name,related_to,'global')
          db.toplevel = top_key
          cls.get_or_insert(top_key.id(),tag_name=tag_name,related_to=related_to,\
            collection='global',cnt=0)
      db.incr(_incr_step)


      if db.count <= 0:
        keys_del.append(db.key)
        if getattr(db,"toplevel",None):
          db_top = db.toplevel.get()
          if db_top.count <= 1: # its 0 after put()
            keys_del.append(db.toplevel)
      else:
        dbs_new.append(db)
    ndb.delete_multi(keys_del) #TODO async delete
    return ndb.put_multi(dbs_new)

  @classmethod
  def add(cls, tag_names, collection=None):
    """Add relations by a tag list"""
    if not tag_names:
      return []
    keys = TagRelation.generate_all_keys(tag_names,collection)
    #print "Keys to add for relation"
    #print keys
    return cls.add_by_keys(keys)

  @classmethod
  def remove(cls, tag_names, collection=None):
    """Remove relations by a tag list"""
    if not tag_names:
      return []
    keys = TagRelation.generate_all_keys(tag_names,collection)
    cls.add_by_keys(keys,_incr_step=-1)
    return keys


  @classmethod
  def qry(cls, tag_name=None, related_to=None, toplevel=None, \
      collection=None,  order_by_count=True, **kwargs):
    """Query for the icon model"""
    qry = cls.query(**kwargs)
    if tag_name:
      qry_tmp = qry
      qry = qry.filter(cls.tag_name==tag_name.lower())
    if toplevel:
      qry_tmp = qry
      qry = qry.filter(cls.toplevel==toplevel)
    if related_to:
      qry_tmp = qry
      qry = qry.filter(cls.related_to==related_to.lower())
    if collection:
      qry_tmp = qry
      qry = qry.filter(cls.collection == collection)
    if order_by_count:
      qry_tmp = qry
      qry = qry.order(-cls.cnt)
    #else filter for private True and False
    return qry


  @staticmethod
  def print_list(dbs):
    print "\n+-------------------+-------------------+-------------------+-----------+---"
    print "| {:<18}| {:<18}| {:<18}| {:<10}| {:<48}".\
        format("tag", "related to", "collection", "count", "toplevel")
    print "+-------------------+-------------------+-------------------+-----------+---"
    for db in dbs:
      print "| {:<18}| {:<18}| {:<18}| {:<10}| {:<48}".\
          format(db.tag_name, db.related_to, db.collection, db.count, db.toplevel or "")
    print "+-------------------+-------------------+-------------------+-----------+---"
    print
    print

  @classmethod
  def get_dbs(
      cls, tag_name=None, related_to=None, collection=None,
      toplevel=None, **kwargs
    ):
    return super(TagRelation, cls).get_dbs(
        tag_name=tag_name or util.param('tag_name', str),
        related_to=related_to or util.param('related_to', bool),
        collection=collection or util.param('collection', str),
        toplevel=toplevel or util.param('toplevel', ndb.Key),
        **kwargs
      )


class Taggable(ndb.Model): # use the counter mixin
  """Adds a tags property

  Tags are managed in the 'Tag' model, this mixin
  adds two methods to deal with tags:
    'add_tags': if an tag already exists it can be added by its key
    'create_tags': create a new tag

  The two method 'put' the tag automatically, this means it is recommended to
  put the taggable model as well or remove the tags again if something went wrong.
    """
  #tags = ndb.StringProperty(TagStructure, repeated=True)
  tags = ndb.StringProperty(indexed=True, repeated=True,
      validator=lambda p, v: v.lower())
  _MAX_TAGS = 20
  #_new_tags = []

  def add_tags(self, tags):
    """Adds a tags as strings.

    Color and icon are saved in the 'Tag' model.
    All tag names are change to lower letters and double entries are deleted."""
# TODO if icon changes it could give double entries, not good!
    new_tags = []
    if not getattr(self,'collection',None):
      col = 'global'
    else:
      col = self.collection
    if getattr(self,'tags',None):
      #print "Check if tags already exist"
      for tag in tags:
        if tag not in self.tags:
          new_tags.append(tag)
      #new_tags = self.tags - tags
    else:
      new_tags = tags
    #print new_tags
    if len(self.tags) + len(new_tags) > self._MAX_TAGS:
      raise UserWarning('Too many tags, maximum {} tags are allowed, {} are used.'.\
          format(self._MAX_TAGS,len(self.tags) + len(new_tags)))
    for tag in new_tags:
      #Tag.add(tag.name, icon_structure=tag.icon, color=tag.color, collection=col)
      Tag.add(tag, collection=col)

    ## Add relations
    #old_tagnames = Tag.tag_structures_to_tagnames(self.tags)
    old_tagnames = self.tags[:]
    self.tags.extend(new_tags)
    #new_tagnames = Tag.tag_structures_to_tagnames(self.tags)
    new_tagnames = self.tags[:]
    #print "Add new relation names"
    #print new_tagnames
    TagRelation.remove(old_tagnames,col)
    TagRelation.add(new_tagnames,col)

    return self.tags

  def remove_tags(self, tags):
    """Removes tags as strings. """
# TODO if icon is different it could give wrong entries, not good!
# only compare names!

    rm_tags = []
    new_tags = []
    if not getattr(self,'collection',None):
      col = 'global'
    else:
      col = self.collection
    if not getattr(self,'tags',None):
      #print "Check if tags already exist"
      return []
    else:
      for tag in tags:
        if tag in self.tags:
          rm_tags.append(tag)
    #print "Tags to remove"
    #print rm_tags
    for tag in rm_tags:
      #Tag.remove(tag.name, collection=col)
      Tag.remove(tag, collection=col)

    ## Del relations
    #old_tagnames = Tag.tag_structures_to_tagnames(self.tags)
    old_tagnames = self.tags
    # remove tags
    still_tags = []
    for tag in self.tags:
      if tag not in rm_tags:
        still_tags.append(tag)
    self.tags = still_tags
    #new_tagnames = Tag.tag_structures_to_tagnames(self.tags)
    new_tagnames = self.tags
    #print "Tags to remove (Rel):"
    #print old_tagnames
    TagRelation.remove(old_tagnames,col)
    #print "Tags to add (Rel):"
    #print new_tagnames
    TagRelation.add(new_tagnames,col)


  def update_tags(self,tags):
    """Updates the tag list, a full tag list is required.

    The function adds, removes, and reorders the tag list"""
    # make list unique, no double entries
    tags_unique = []
    for tag in tags:
      if tag not in tags_unique:
        tags_unique.append(tag.lower())
    tags = tags_unique
    add_tags = []
    rm_tags = []
    if not getattr(self,'tags',None):
      self.tags = []

    for tag in tags: # look which tags to add
      if tag not in self.tags:
        add_tags.append(tag)

    for tag in self.tags: # look which tags to remove
      if tag not in tags:
        rm_tags.append(tag)

    self.add_tags(add_tags)
    self.remove_tags(rm_tags)

    self.tags = tags
    return self.tags

