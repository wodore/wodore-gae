"""
From blog post: http://brianmhunt.github.io/articles/ndb-tags/
License: MIT <http://brianmhunt.mit-license.org/>
"""

from google.appengine.ext import ndb


MAX_TAGS_FOR_TAGGABLE = 15
POPULAR_PAGE_SIZE = 30

class _Tag(ndb.Model): # use the counter mixin
    """Basic tag class, the tag name is used as key.
    """
    # Multiply tags can belong to one collection, for example an user group.
    # It needs to be a key in order  to not to have different collections
    # with the same name.
# TODO make it a string, it's recommanded to safe url safe keys
# TODO make it possible to change the global name (default='global')
    collection = ndb.KeyProperty(required=True, indexed=True,
                            #default='global',
                             validator=lambda p, v: v.lower())
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    private = ndb.BooleanProperty(required=True,default=False)

class _TagCount(_Tag): # use the counter mixin
    """Saves a tag with a counter, the tag name is used as key.
    """
    count = ndb.IntegerProperty(default=0, indexed=True)


class _IconStructure(ndb.Model): # use the counter mixin
    """Basic icon class
    """
    name = ndb.StringProperty(indexed=True)
    data = ndb.BlobProperty()
    external_source = ndb.StringProperty(indexed=False) # not recommended
    filetype = ndb.StringProperty(choices=['svg','png','external'],indexed=True,
                              required=True)
class Iconize(ndb.Model): # use the counter mixin
    icon = ndb.StructuredProperty(_IconStructure)

class _TagIcon(_Tag,Iconable): # use with icon mixin
    """Saves a tag with a corresponding icon, the tag name is used as key.
    """
    name = ndb.StringProperty(indexed=True)
    count = ndb.IntegerProperty(default=0, indexed=True)


class Taggable(object):
    """A mixin that adds taggability to a class.

    Adds a 'tags' property.
    """
    tags = ndb.StringProperty(repeated=True, indexed=True)

    def _post_get_hook(self, future):
        """Set the _tm_tags so we can compare for changes in pre_put
        """
        self._tm_tags = future.get_result().tags

    def _post_put_hook(self, future):
        """Modify the associated Tag instances to reflect any updates
        """
        old_tagset = set(getattr(self, '_tm_tags', []))
        new_tagset = set(self.tags)

        # These are tags that have changed
        added_tags = new_tagset - old_tagset
        deleted_tags = old_tagset - new_tagset

        # Get the key for this post
        self_key = future.get_result()

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
        self._tm_tags = self.tags
