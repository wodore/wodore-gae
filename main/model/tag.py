from google.appengine.ext import ndb

from counter import CountableLazy
from icon import IconStructure, Iconize

"""
A tag consists of two model classes:
  TagStructure: Which holds all tag specific data but no additional information.
  Tag: The 'Tag' model contains additional information for a tag like a counter
       and collection. A 'TagStructure' is return by 'get_tag()'.

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

class Tag(Iconize, CountableLazy, ndb.Model):
  """Tag Model
  The key should have the following from: tag__{name}_{collection}"""
  name = ndb.StringProperty(indexed=True,required=True)
  color = ndb.StringProperty(indexed=True,required=True,default='blue')
  approved = ndb.BooleanProperty(required=True,default=False)
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  # Preferred urlsafe keys
  collection = ndb.StringProperty(required=True, indexed=True,
                  default='global', validator=lambda p, v: v.lower())
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

  @staticmethod
  def tag_to_keyname(name,collection=None):
    """Returns a key name (string)"""
    col = collection or 'global'
    return "tag__{}_{}".format(name.lower(), col)

  @staticmethod
  def tag_to_key(name, collection=None):
    """Returns a key"""
    return ndb.Key("Tag", Tag.tag_to_keyname(name,collection))


  @classmethod
  def add(cls,name,collection=None, toplevel_key=None, icon_key=None, \
      icon_structure=None, force_new_icon=False, auto_incr=True):
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
      order_by_count=True, **kwargs):
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
    if only_approved:
      qry_tmp = qry
      qry = qry_tmp.filter(cls.approved==True)
    if order_by_count:
      qry_tmp = qry
      qry = qry.order(-cls.cnt)
    #else filter for private True and False
    return qry


class TagRelation(CountableLazy, ndb.Model): # use the counter mixin
  """Tag relation model

  key: tagrel__{tag_name}_{relate_to}_{collection}
  """
  tag_name = ndb.StringProperty(indexed=True,required=True)
  related_to = ndb.StringProperty(indexed=True,required=True)
  collection = ndb.StringProperty(indexed=True,required=True,default='global')

  @staticmethod
  def to_keyname(tag_name,related_to,collection=None):
    """Returns a key name (string)"""
    col = collection or 'global'
    return "tagrel__{}_{}_{}".format(tag_name.lower(),related_to.lower(), col)

  @staticmethod
  def to_key(tag_name, related_to, collection=None):
    """Returns a key"""
    return ndb.Key("TagRelation", cls.to_keyname(tag_name,related_to,collection))


  @classmethod
  def generate_all_keys(tag_names, collection=None):
    keys = []
    for tag_name in tag_names:
      keys.append(cls.generate_related_keys(tag_name,tag_names,collection))
    return keys

  @classmethod
  def generate_related_keys(cls,tag_name,related_tos,collection=None):
    keys = []
    for related_to in related_tos:
      if related_to != tag_name:
        keys.append(cls.to_key(tag_name,related_to,collection))

    return keys






class Taggable(ndb.Model): # use the counter mixin
  """Adds a tags property

  Tags are managed in the 'Tag' model, this mixin
  adds two methods to deal with tags:
    'add_tags': if an tag already exists it can be added by its key
    'create_tags': create a new tag

  The two method 'put' the tag automatically, this means it is recommended to
  put the taggable model as well or remove the tags again if something went wrong.
    """
  tag = ndb.StructuredProperty(TagStructure)

  def add_tags(self, key):
    """Adds a tags by name. """
    if not getattr(self,'collection',None):
      col = 'global'
    else:
      col = self.collection
    key = Tag.add(key,collection=col)
    self.icon = key.get().get_tag()

#  def create_icon(self,icon,name,private=False):
#    if not getattr(self,'collection',None):
#      col = 'global'
#    else:
#      col = self.collection
#    key = Icon.create(icon=icon,name=name,collection=col,private=private)
#    icon.icon_key = key
#    self.icon = icon

  def remove_tags(self):
    if getattr(self,'tag',None):
      #Icon.remove(self.tag.tag_key)
## TODO add decr of tag counter
      del self.tag

