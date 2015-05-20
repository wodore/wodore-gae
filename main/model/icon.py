from google.appengine.ext import ndb

from counter import CountableLazy

"""
An icon consists of two model classes:
  IconStructure: Which helds all icon specific data but no additional information.
  Icon: The Icon model contains an IconStructure as an icon and additional information
        like a counter and collection.

For each icon exists a toplevel icon which can have children grouped by collection.
Once an icon is created it should not be changed anymore.
If one of the childrens counter is updated the topevel icon's counter is updated
as well.
The highest toplevel has the default collection 'global'.
"""


class IconStructure(ndb.Model): # use the counter mixin
  """Basic icon class
  """
  icon_key = ndb.KeyProperty(required=False)
  name = ndb.StringProperty(indexed=True)
  data = ndb.BlobProperty()
  external_source = ndb.StringProperty(indexed=False) # not recommended
  filetype = ndb.StringProperty(choices=['svg','png','external'],indexed=True,
                     default='svg', required=True)

class Icon(CountableLazy, ndb.Model):
  icon = ndb.StructuredProperty(IconStructure)
  private = ndb.BooleanProperty(required=True,default=False)
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  # Preferred urlsafe keys
  collection = ndb.StringProperty(required=True, indexed=True,
                  default='global', validator=lambda p, v: v.lower())
  # Key the the parent (or toplevel) entry. If empty it is already the toplevel,
  # usually the collection 'global'
  toplevel = ndb.KeyProperty()
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
  def create(cls,icon,collection='global',toplevel=None,private=False, auto=True):
    """ Creates and puts a new icon to the database.
    Returns Icon key"""
    new_icon = Icon(icon = icon,
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

    1. If the key's collection is 'global' (not toplevel) or 'as_child' is true:
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
      if collection == 'global':
        return self.add(icon_db.toplevel,collection)
      elif icon_db.collection == 'global' or as_child:
        toplevel = key
      else:
        toplevel = icon_db.toplevel

    ## Look for icons with same toplevel and collection
    keys = Icon.by_toplevel(toplevel, collection=collection, keys_only=True)
    if keys:
      #for key in keys:
      key = keys
      return Icon.add(key,collection)
    else:
      return Icon.create(icon_db.icon,collection=collection,toplevel=toplevel)




  @classmethod
  def by_toplevel(cls, toplevel, collection=None, private=False, keys_only=False):
    """Returns a icon keys defined by its toplevel and some addition parameters"""
# TODO implement this method, maybe even a low level method first
    return cls.query(cls.toplevel==toplevel,cls.collection==collection).order(-cls.cnt).get( keys_only=keys_only)
    return False


  def _add_and_put(self, auto=True):
    """ Adds and puts an icon to the DB

    If 'auto' is true it automatically creates a toplevel icon if none is given.
    This only works for one level, if a higher hierarchy is required it needs to be
    done manually.
    """
    if not getattr(self,'toplevel',None) and self.collection != 'global' and auto: #\
      top = Icon(icon=self.icon)
      top_key = top.put()
      self.toplevel = top_key

    self.incr()
    self.put()
    self.get_icon()
    return self.key







class Iconize(ndb.Model): # use the counter mixin
  icon = ndb.StructuredProperty(IconStructure)

  def _post_get_hook(self, future):
    """Set the _tm_tags so we can compare for changes in pre_put
    """
    self._tm_icon = future.get_result().icon

  def _post_put_hook(self, future):
    """Modify the associated Tag instances to reflect any updates
    """
    old_icon = getattr(self,'_tm_icon',{})
    new_icon = getattr(self,'icon',{})
    # new icon?
    if old_icon != new_icon:
      # Get the key for this post
      icon = Icon(icon=new_icon)
      icon_key = icon.put()
      self.icon.icon_key = icon_key
      #self_key = future.get_result()

    #@ndb.transactional_tasklet
    #def update_changed(tag):
    #    tag_instance = yield Tag.get_or_create_async(tag)
    #    if tag in added_tags:
    #        yield tag_instance.link_async(self_key)
    #    else:
    #        yield tag_instance.unlink_async(self_key)

    #ndb.Future.wait_all([
    #    update_changed(tag) for tag in added_tags | deleted_tags
    #])

    ## Update for any successive puts on this model.
    self._tm_icon = self.icon
