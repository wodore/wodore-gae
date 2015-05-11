from google.appengine.ext import ndb

from counter import CountableLazy



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

  def get_icon(self):
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

  def add(cls,key=None,collection='global',toplevel=None):
    if key:
      icon_db = key.get()
      if icon_db.collection == collection:
        icon_db.incr()
        icon_db.put()
      else:
        pass
        #TODO: check if colleciton already exists
        # If not create a new icon
    elif toplevel:
      pass
      #TODO: Look for entries with smae toplevel and colection
      #      If any exist increment them
      #      Else create new one



  def _add_and_put(self, auto=True):
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
