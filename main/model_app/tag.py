# coding: utf-8

from __future__ import absolute_import
import numbers


class Tag(object):
  def __init__(self, name, style={}, group=[], status="LOCAL"):
    """Creates a tag object

    A tag object is used to store and retrieve information t oa tag from a DB.

    Args:
      name (str): Tag name, it is converted to a string.
      style (dict): style dictionary.
      group (list | tuple): a list with group levels. Eg. ``['first','2nd']``
      status ("LOCAL" | "PUBLIC"): Status of the tag, ``LOCAL`` means it is
                                   not approved yet for ``PUBLIC`` use.
      """
    self._name = str(name)
    self._style = style
    self._group = group
    self._status = status
    self._counter = 0
    self._renamed = False

  @property
  def name(self):
    """Tag name """
    return self._name

  @name.setter
  def name(self,new_name):
    """The tag name cannot be set directly, us 'rename' instead"""
    raise AttributeError("can't set attribute, use 'rename(new_name)' instead")

  def rename(self, new_name):
    """Rename the tag

    If the tag is added (``add()``) the old name's counter is deacreased and the
    new name increaded."""
    if not self._renamed:
      self._old_name = self._name
    self._name = str(new_name)
    return self._name

  @property
  def style(self):
    """Tag style"""
    return self._style

  @style.setter
  def style(self, style, group):
    self._style = style
    return self._style

  def set_related_to(self, tag_names):
    """Add related tags

    Args:
      tag_names (list | tuple): A list with the names as string or Tag object"""
    # Add to related_to_db
    return tag_names

  def remove_related_to(tag_names):
    """Remove related tags

    Args:
      tag_names (list | tuple): A list with the names as string or Tag object"""
    # Remove from related_to_db
    return tag_names

  @property
  def status(self):
    """Tag status"""
    return self._status

  @status.setter
  def status(self, status):
    self._status = status
    return self._status

  @property
  def counter(self,all=False):
    """Tag counter

    TODO: return an array with the counters (depending on groups)
    Returns:
      If all is ``True`` it returns a array with a counter for each group,
      otherwise just for the current group (as integer)."""
    if all:
      return [self._counter]
    else:
      return self._counter

  def add(self):
    """Add the tag to the database"""
    if self._renamed:
      old_tag = Tag(self._old_name)
      old_tag.remove()
    self._incr_counter(1)
    return self._counter

  def remove(self):
    """Remove the tag from the database"""
    if self._counter > 0:
      self._decr_counter(1)
    return self._counter

  def _incr_counter(self, incr=1):
    self._counter += incr
    return self._counter

  def _decr_counter(self, decr=1):
    self._counter -= decr
    return self._counter

