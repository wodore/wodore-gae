# coding: utf-8

from __future__ import absolute_import

class Tag(object):
  def __init__(self, name, style, group=[], status="LOCAL", counter=1):
    self.name = name
    self.style = style
    self.group = group
    self.status = status
    self.counter = counter

  def get_name(self):
    return self.name

  def set_name(self, name):
    self.name = name
    return self.name

  def set_style(self, style, group):
    self.style = style
    return self.style

  def set_related_to(self, tag_names):
    # Add to related_to_db
    return tag_names

  def remove_related_to(tag_names)
    # Remove from related_to_db
    return tag_names

  def get_status(self):
    return self.status

  def set_status(self, status):
    self.status = status
    return self.status

  def get_counter(self):
    return self.counter

  def _incr_counter(self, incr=1):
    self.counter += incr
    return self.counter

  def _decr_counter(self, decr=1):
    self.counter -= decr
    return self.counter

