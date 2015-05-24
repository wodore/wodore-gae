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
    self.L1 = 4
    self.L2 = 5


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
    i = 0
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(top_dbs[0].count,1)
    self.assertEqual(top_dbs[10],None)
    self.assertEqual(top_dbs[14],None)


  def test_query_icon_relation(self):
    #keys = TagRelation.add(self.tag_list1,collection='child1')
    L1 = self.L1 # save length of the lists
    L2 = self.L2
    L12 = L1 + L2
    L1e = L1 * (L1-1) # all entries
    L2e = L2 * (L2-1) # all entries
    L12e = L12 * (L12-1) # all entries
    keys_child1 = TagRelation.add(self.tag_list2+self.tag_list1,collection='child1')
    keys_child2 = TagRelation.add(self.tag_list2,collection='child2')
    keys_top1 = TagRelation.add(self.tag_list1)
    keys_top1 = TagRelation.add(self.tag_list1)
# query for all
    dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(dbs)
    self.assertEqual(len(dbs),2*L12e+L2e)
    self.assertEqual(dbs[0].count,3)
    self.assertEqual(dbs[-1].count,1)
# query only for a child
    dbs_child1 = TagRelation.qry(collection='child1').fetch()
    self.assertEqual(len(dbs_child1),L12e)
# query only for one tag name
    dbs_A = TagRelation.qry(tag_name='A').fetch()
    #TagRelation.print_list(dbs_A)
    self.assertEqual(len(dbs_A),(L12-1)*2+(L2-1))
# query for one tag name and collection
    dbs_A_child1 = TagRelation.qry(tag_name='A',collection='child1').fetch()
    #TagRelation.print_list(dbs_A_child1)
    self.assertEqual(len(dbs_A_child1),(L12-1))

# query only for one tag relation
    dbs_A = TagRelation.qry(related_to='A').fetch()
    #TagRelation.print_list(dbs_A)
    self.assertEqual(len(dbs_A),(L12-1)*2+(L2-1))
# query for one tag name and collection
    dbs_A_child1 = TagRelation.qry(related_to='A',collection='child1').fetch()
    #TagRelation.print_list(dbs_A_child1)
    self.assertEqual(len(dbs_A_child1),(L12-1))

## Order by tag_name
    dbs = TagRelation.qry(order_by_count=False).order(TagRelation.tag_name).fetch()
    #TagRelation.print_list(dbs)
    self.assertEqual(len(dbs),2*L12e+L2e)
    self.assertEqual(dbs[0].tag_name,'a')
    self.assertEqual(dbs[-1].tag_name,'two')

class TestTagModel(Taggable, ndb.Model):
  """This is a test class for trying out tags
  """
  name = ndb.StringProperty()
  collection = ndb.StringProperty()


class TestTaggable(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    self.icon1 = IconStructure(data='i1')
    self.icon2 = IconStructure(data='i2')
    self.icon3 = IconStructure(data='i3')
    #self.tag1 = TagStructure(name='one', icon=self.icon1, color='red')
    #self.tag2 = TagStructure(name='Two', icon=self.icon2, color='green')
    #self.tag3 = TagStructure(name='Three', icon=self.icon3, color='blue')
    #self.tag4 = TagStructure(name='four')
    #self.tags1 = [self.tag1,self.tag2,self.tag3, self.tag4]
    # Create tags
    Tag.add(name='one', icon_structure=self.icon1, color='red', auto_incr=False)
    Tag.add(name='Two', icon_structure=self.icon2, color='green', auto_incr=False)
    Tag.add(name='three', icon_structure=self.icon3, color='blue', auto_incr=False)

    self.tag1 = 'one'
    self.tag2 = 'Two'
    self.tag3 = 'Three'
    self.tag4 = 'four'
    self.tags1 = [self.tag1,self.tag2,self.tag3, self.tag4]

  def test_init_taggable(self):
    demo1 = TestTagModel(name='demo1')
    demo1.put()
    assert demo1 is not None
    self.assertEqual(demo1.name, 'demo1')

  def test_add_tag(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags([self.tag1])
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 1)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 0)
    #TagRelation.print_list(rel_dbs)

    demo1.add_tags([self.tag2, self.tag3])
    # show tags
    tag_dbs = Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 3)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 6)
    #TagRelation.print_list(rel_dbs)

    demo1.add_tags(self.tags1)
    # show tags
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs), 4)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 4*3)
    #TagRelation.print_list(rel_dbs)

  def test_add_tag_with_collection(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags([self.tag1])
    demo1.put()
    demo1a = TestTagModel(name='demo1a',collection='demo1a')
    demo1a.add_tags([self.tag1])
    demo1a.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs), 2)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs), 0)

    demo1a.add_tags([self.tag2, self.tag3])
    # show tags
    tag_dbs = Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 6)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 6*2)
    #TagRelation.print_list(rel_dbs)

  def test_add_to_much_tags(self):
    demo1 = TestTagModel(name='demo1')
    # create a long list of tags
    tags = []
    for i in range (0,50):
      tags.append(TagStructure(name=str(i)))
    with self.assertRaises(UserWarning):
      demo1.add_tags(tags)
    demo1.put()

  def test_remove_tags(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags(self.tags1)
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)

    demo1.remove_tags([self.tag1,self.tag2])
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry(count_greater=-10).fetch()
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(tag_dbs[-1].count,0)
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 2)
    #TagRelation.print_list(rel_dbs)

  def test_remove_tags_with_collection(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags(self.tags1)
    demo1.put()
    demo1a = TestTagModel(name='demo1a',collection='demo1a')
    demo1a.add_tags(self.tags1)
    demo1a.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)

    demo1a.remove_tags([self.tag1,self.tag2])
    demo1a.put()
    # show tags and relations
    tag_dbs = Tag.qry(count_greater=-10).fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,2)
    self.assertEqual(tag_dbs[-1].count,0)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs), 3*4+2)

  def test_update_tags(self):
    demo1 = TestTagModel(name='demo1')
    demo1.update_tags(self.tags1)
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(len(tag_dbs),4)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(rel_dbs[0].count,1)
    self.assertEqual(len(rel_dbs),4*3)
    # Add the same, nothing should happen.
    demo1.update_tags(self.tags1)
    demo1.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(len(tag_dbs),4)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(rel_dbs[0].count,1)
    self.assertEqual(len(rel_dbs),4*3)

    ## Remove tags
    demo1.update_tags([self.tag1,self.tag2])
    demo1.put()
    self.assertEqual(demo1.tags[0],'one')
    self.assertEqual(demo1.tags[1],'two')
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(tag_dbs[-1].count,1)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs),2*1)

    # Add and remove and change order
    demo1.update_tags([self.tag3,self.tag2])
    demo1.put()
    self.assertEqual(demo1.tags[0],'three')
    self.assertEqual(demo1.tags[1],'two')
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(tag_dbs[-1].count,1)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs),2*1)

    # With collection
    demo1a = TestTagModel(name='demo1a', collection='1a')
    demo1a.update_tags(self.tags1+[self.tag1])
    demo1a.put()
    # show tags and relations
    tag_dbs = Tag.qry().fetch()
    #Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs),8)
    rel_dbs = TagRelation.qry().fetch()
    #TagRelation.print_list(rel_dbs)
    self.assertEqual(rel_dbs[0].count,3)
    self.assertEqual(len(rel_dbs),2*4*3)


if __name__ == "__main__":
  unittest.main()
