import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
sys.path.append('./')
sys.path.append('./model')

#import logging
import unittest
from google.appengine.ext import ndb#, testbed


from tag import Taggable, TagStructure, Tag, TagRelation
from icon import Icon, IconStructure
#from counter import CountableLazy


class TestTag(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    pass

  def test_init_tag(self):
    tag1 = Tag(name='tag1')
    tag1.put()
    assert tag1 is not None
    self.assertEqual(tag1.name, 'tag1')


  def test_add_tag(self):
    key1 = Tag.add('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.count, 1)
    key1a = Tag.add('one','child1')
    key1a = Tag.add('one','child1')
    key1b = Tag.add('one','child2')
    key1bA = Tag.add('one','child2A',key1b)
    tag1_db = key1.get()
    tag1a_db = key1a.get()
    tag1b_db = key1b.get()
    tag1bA_db = key1bA.get()
    self.assertEqual(tag1_db.count, 5)
    self.assertEqual(tag1a_db.count, 2)
    self.assertEqual(tag1b_db.count, 2)
    self.assertEqual(tag1b_db.toplevel, key1)
    self.assertEqual(tag1bA_db.toplevel, key1b)

## Add a child without a parent
    #print tag1_db.get_tag()
    key2a = Tag.add('two','child1')
    tag2a_db = key2a.get()
    self.assertEqual(tag2a_db.count, 1)
    key2a = Tag.add('two','child2')
    self.assertEqual(Tag.tag_to_key('two').get().count, 2)

  def test_add_tag_with_icon_structure(self):
    icon1 = IconStructure(data='i')
    key1 = Tag.add('one', icon_structure=icon1)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.icon, icon1)

    icon2 = IconStructure(data='o')
    key1 = Tag.add('one', icon_structure=icon2)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.icon, icon1)

    key1 = Tag.add('one', icon_structure=icon2, force_new_icon=True, auto_incr=False)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.icon, icon2)
    self.assertEqual(tag1_db.count, 2)

  def test_add_tag_with_icon_key(self):
    icon1 = IconStructure(data='i')
    icon1_db = Icon(icon=icon1,name='one')
    icon1_key = icon1_db.put()
    key1 = Tag.add('one', icon_key=icon1_key)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.icon, icon1)


  def test_remove_tag_with_icon(self):
    icon1 = IconStructure(data='i')
    icon1_db = Icon(icon=icon1,name='one')
    icon1_key = icon1_db.put()
    key1 = Tag.add('one',icon_key=icon1_key)
    self.assertEqual(icon1_key.get().count, 1)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.count, 1)
    Tag.remove('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.count, 0)
    self.assertEqual(icon1_key.get().count, 0)


  def test_approve_tag(self):
    key1 = Tag.add('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.approved, False)
    Tag.approve('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.approved, True)


class TestTagRelation(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True
  def setUp(self):
    self.tag_list1 = ['one','two','three','four']
    self.tag_list2 = ['A','B','C','D','E']


  def test_init_tag_relation(self):
    tagRel1 = TagRelation(tag_name='tag1',related_to='tagA')
    key = tagRel1.put()
    assert tagRel1 is not None
    tag_rel = key.get()
    self.assertEqual(tag_rel.tag_name, 'tag1')
    self.assertEqual(tag_rel.related_to, 'tagA')

  def test_to_and_from_key(self):
    n = 'n'
    r = 'r'
    c = 'c'
    key = TagRelation.to_key(n,r,c)
    n2,r2,c2 = TagRelation.from_key(key)
    self.assertEqual(n, n2)
    self.assertEqual(r, r2)
    self.assertEqual(c, c2)

  def test_generate_all_keys_and_add(self):
    # Generate all keys
    keys = TagRelation.generate_all_keys(self.tag_list1)
    self.assertEqual(len(keys), len(self.tag_list1)*(len(self.tag_list1)-1))
    # Add by keys
    TagRelation.add_by_keys(keys)
    dbs = ndb.get_multi(keys)
    for db in dbs:
      self.assertEqual(db.count,1)
    # Partially add again
    TagRelation.add_by_keys(keys[3:5])
    dbs = ndb.get_multi(keys)
    for db in dbs[3:5]:
      self.assertEqual(db.count,2)
    for db in dbs[6:]:
      self.assertEqual(db.count,1)
    # Add a child to the same list
    keys2 = TagRelation.add(self.tag_list1,collection='child')
    self.assertEqual(len(keys2), len(self.tag_list1)*(len(self.tag_list1)-1))
    dbs = ndb.get_multi(keys)
    for db in dbs[7:]:
      self.assertEqual(db.count,2)
    # add a child with a new list
    keys3 = TagRelation.add(self.tag_list2,collection='child')
    self.assertEqual(len(keys3), len(self.tag_list2)*(len(self.tag_list2)-1))
    dbs = ndb.get_multi(keys3)
    for db in dbs:
      self.assertEqual(db.count,1)
    # check also toplevels
    top_keys3 = TagRelation.generate_all_keys(self.tag_list2)
    top_dbs = ndb.get_multi(top_keys3)
    for db in top_dbs:
      self.assertEqual(db.count,1)

  def test_remove(self):
    keys = TagRelation.add(self.tag_list2,collection='child')
    keys_rm = TagRelation.remove(self.tag_list2[2:4],collection='child')
    dbs_rm = ndb.get_multi(keys_rm)
    for db in dbs_rm:
      self.assertEqual(db,None)
    top_keys = TagRelation.generate_all_keys(self.tag_list2)
    top_dbs = ndb.get_multi(top_keys)
    self.assertEqual(top_dbs[0].count,1)
    self.assertEqual(top_dbs[10],None)
    self.assertEqual(top_dbs[14],None)



if __name__ == "__main__":
  unittest.main()
