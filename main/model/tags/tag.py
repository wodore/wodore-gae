# coding: utf-8

from __future__ import absolute_import

class Tag(object):
  def __init__(self, name, style, group=[], status="LOCAL", counter=1):
    self._name = name
    self._style = style
    self._group = group
    self._status = status
    self._counter = counter

  def get_name(self):
    return self._name

  def set_name(self, name):
    self._name = name
    return self._name

  def set_style(self, style, group):
    self._style = style
    return self._style

  def set_related_to(self, tag_names):
    # Add to related_to_db
    return tag_names

  def remove_related_to(tag_names)
    # Remove from related_to_db
    return tag_names

  def get_status(self):
    return self._status

  def set_status(self, status):
    self._status = status
    return self._status

  def get_counter(self):
    return self._counter

  def _incr_counter(self, incr=1):
    self._counter += incr
    return self._counter

  def _decr_counter(self, decr=1):
    self._counter -= decr
    return self._counter

