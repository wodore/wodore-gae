import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
#sys.path.append('./')
#sys.path.append('./model')

#import logging
import unittest
from google.appengine.ext import ndb#, testbed


#from tag import Taggable, TagStructure, Tag, TagRelation
#from icon import Icon, IconStructure
#from counter import CountableLazy


class TestTag(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    global config
    global model
    import config
    import model
    self.colg = model.Collection.top_key()

    self.child1 = ndb.Key('Collection','child1')
    self.child1a = ndb.Key('Collection','child1a')
    self.child2 = ndb.Key('Collection','child2')
    self.child2a = ndb.Key('Collection','child2a')

  def test_init_tag(self):
    tag1 = model.Tag(name='tag1')
    tag1.put()
    assert tag1 is not None
    self.assertEqual(tag1.name, 'tag1')


  def test_add_tag(self):
    key1 = model.Tag.add('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.count, 1)
    key1a = model.Tag.add('one',self.child1)
    key1a = model.Tag.add('one',self.child1)
    key1b = model.Tag.add('one',self.child2)
    key1bA = model.Tag.add('one',self.child2a,key1b)
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
    key2a = model.Tag.add('two',self.child1)
    tag2a_db = key2a.get()
    self.assertEqual(tag2a_db.count, 1)
    key2a = model.Tag.add('two',self.child2)
    self.assertEqual(model.Tag.tag_to_key('two').get().count, 2)

  def test_add_tag_with_icon_structure(self):
    icon1 = 'i'
    key1 = model.Tag.add('one', icon_data=icon1)
    tag1_db = key1.get()
    self.assertEqual(model.Icon.get_by_id(tag1_db.icon_id).icon, icon1)

    icon2 = 'o'
    key1 = model.Tag.add('one', icon_data=icon2)
    tag1_db = key1.get()
# if not forced icon should not be overwritten
    self.assertEqual(model.Icon.get_by_id(tag1_db.icon_id).icon, icon1)

    key1 = model.Tag.add('one', icon_data=icon2, force_new_icon=True, auto_incr=False)
    tag1_db = key1.get()
    self.assertEqual(model.Icon.get_by_id(tag1_db.icon_id).icon, icon2)
    self.assertEqual(tag1_db.count, 2)

  def test_add_tag_with_icon_key(self):
    icon1 = 'i'
    icon1_db = model.Icon(icon=icon1,name='one')
    icon1_key = icon1_db.put()
    key1 = model.Tag.add('one', icon_key=icon1_key)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.icon_id, icon1_key.id())


  def test_remove_tag_with_icon(self):
    icon1 = 'i'
    icon1_db = model.Icon(icon=icon1,name='one')
    icon1_key = icon1_db.put()
    key1 = model.Tag.add('one',icon_key=icon1_key)
    self.assertEqual(icon1_key.get().count, 1)
    tag1_db = key1.get()
    self.assertEqual(tag1_db.count, 1)
    model.Tag.remove('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.count, 0)
    self.assertEqual(icon1_key.get().count, 0)


  def test_approve_tag(self):
    key1 = model.Tag.add('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.approved, False)
    model.Tag.approve('one')
    tag1_db = key1.get()
    self.assertEqual(tag1_db.approved, True)

#  def test_get_dbs_tag(self):
#    # SEE http://flask.pocoo.org/docs/0.10/testing/
#    key1 = model.Tag.add('one')
#    key1a = model.Tag.add('one',self.child1)
#    key1a = model.Tag.add('one',self.child1)
#    key1b = model.Tag.add('one',self.child2)
#    key1 = model.Tag.add('two')
#    key1a = model.Tag.add('two',self.child1)
#    dbs = model.Tag.get_dbs()
#    model.Tag.print_list(dbs)
#    self.assertEqual(len(dbs),5)
#
#
#    tag1_db = key1.get()
#    tag1a_db = key1a.get()
#    tag1b_db = key1b.get()
#    tag1bA_db = key1bA.get()
#    self.assertEqual(tag1_db.count, 5)
#    self.assertEqual(tag1a_db.count, 2)
#    self.assertEqual(tag1b_db.count, 2)
#    self.assertEqual(tag1b_db.toplevel, key1)
#    self.assertEqual(tag1bA_db.toplevel, key1b)


class TestTagRelation(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True
  def setUp(self):
    global config
    global model
    import config
    import model
    self.tag_list1 = ['one','two','three','four']
    self.tag_list2 = ['A','B','C','D','E']
    self.L1 = 4
    self.L2 = 5

    self.child1 = ndb.Key('Collection','child1')
    self.child1a = ndb.Key('Collection','child1a')
    self.child2 = ndb.Key('Collection','child2')
    self.child2a = ndb.Key('Collection','child2a')


  def test_init_tag_relation(self):
    tagRel1 = model.TagRelation(tag_name='tag1',related_to='tagA')
    key = tagRel1.put()
    assert tagRel1 is not None
    tag_rel = key.get()
    self.assertEqual(tag_rel.tag_name, 'tag1')
    self.assertEqual(tag_rel.related_to, 'tagA')

  def test_to_and_from_key(self):
    n = 'n'
    r = 'r'
    c = self.child1
    key = model.TagRelation.to_key(n,r,c)
    n2,r2,c2 = model.TagRelation.from_key(key)
    self.assertEqual(n, n2)
    self.assertEqual(r, r2)
    self.assertEqual(c, c2)

  def test_generate_all_keys_and_add(self):
    # Generate all keys
    keys = model.TagRelation.generate_all_keys(self.tag_list1)
    self.assertEqual(len(keys), len(self.tag_list1)*(len(self.tag_list1)-1))
    # Add by keys
    model.TagRelation.add_by_keys(keys)
    dbs = ndb.get_multi(keys)
    for db in dbs:
      self.assertEqual(db.count,1)
    # Partially add again
    model.TagRelation.add_by_keys(keys[3:5])
    dbs = ndb.get_multi(keys)
    for db in dbs[3:5]:
      self.assertEqual(db.count,2)
    for db in dbs[6:]:
      self.assertEqual(db.count,1)
    # Add a child to the same list
    keys2 = model.TagRelation.add(self.tag_list1,collection=self.child1)
    self.assertEqual(len(keys2), len(self.tag_list1)*(len(self.tag_list1)-1))
    dbs = ndb.get_multi(keys)
    for db in dbs[7:]:
      self.assertEqual(db.count,2)
    # add a child with a new list
    keys3 = model.TagRelation.add(self.tag_list2,collection=self.child1)
    self.assertEqual(len(keys3), len(self.tag_list2)*(len(self.tag_list2)-1))
    dbs = ndb.get_multi(keys3)
    for db in dbs:
      self.assertEqual(db.count,1)
    # check also toplevels
    top_keys3 = model.TagRelation.generate_all_keys(self.tag_list2)
    top_dbs = ndb.get_multi(top_keys3)
    for db in top_dbs:
      self.assertEqual(db.count,1)

  def test_remove(self):
    keys = model.TagRelation.add(self.tag_list2,collection=self.child1)
    keys_rm = model.TagRelation.remove(self.tag_list2[2:4],collection=self.child1)
    dbs_rm = ndb.get_multi(keys_rm)
    for db in dbs_rm:
      self.assertEqual(db,None)
    top_keys = model.TagRelation.generate_all_keys(self.tag_list2)
    top_dbs = ndb.get_multi(top_keys)
    i = 0
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(top_dbs[0].count,1)
    self.assertEqual(top_dbs[10],None)
    self.assertEqual(top_dbs[14],None)


  def test_query_icon_relation(self):
    #keys = model.TagRelation.add(self.tag_list1,collection=self.child1)
    L1 = self.L1 # save length of the lists
    L2 = self.L2
    L12 = L1 + L2
    L1e = L1 * (L1-1) # all entries
    L2e = L2 * (L2-1) # all entries
    L12e = L12 * (L12-1) # all entries
    keys_child1 = model.TagRelation.add(self.tag_list2+self.tag_list1,collection=self.child1)
    keys_child2 = model.TagRelation.add(self.tag_list2,collection=self.child2)
    keys_top1 = model.TagRelation.add(self.tag_list1)
    keys_top1 = model.TagRelation.add(self.tag_list1)
# query for all
    dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(dbs)
    self.assertEqual(len(dbs),2*L12e+L2e)
    self.assertEqual(dbs[0].count,3)
    self.assertEqual(dbs[-1].count,1)
# query only for a child
    dbs_child1 = model.TagRelation.qry(collection=self.child1).fetch()
    self.assertEqual(len(dbs_child1),L12e)
# query only for one tag name
    dbs_A = model.TagRelation.qry(tag_name='A').fetch()
    #model.TagRelation.print_list(dbs_A)
    self.assertEqual(len(dbs_A),(L12-1)*2+(L2-1))
# query for one tag name and collection
    dbs_A_child1 = model.TagRelation.qry(tag_name='A',collection=self.child1).fetch()
    #model.TagRelation.print_list(dbs_A_child1)
    self.assertEqual(len(dbs_A_child1),(L12-1))

# query only for one tag relation
    dbs_A = model.TagRelation.qry(related_to='A').fetch()
    #model.TagRelation.print_list(dbs_A)
    self.assertEqual(len(dbs_A),(L12-1)*2+(L2-1))
# query for one tag name and collection
    dbs_A_child1 = model.TagRelation.qry(related_to='A',collection=self.child1).fetch()
    #model.TagRelation.print_list(dbs_A_child1)
    self.assertEqual(len(dbs_A_child1),(L12-1))

## Order by tag_name
    dbs = model.TagRelation.qry(order_by_count=False).order(model.TagRelation.tag_name).fetch()
    #model.TagRelation.print_list(dbs)
    self.assertEqual(len(dbs),2*L12e+L2e)
    self.assertEqual(dbs[0].tag_name,'a')
    self.assertEqual(dbs[-1].tag_name,'two')



class TestTaggable(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    global config
    global model
    import config
    import model

    self.child1 = ndb.Key('Collection','child1')
    self.child1a = ndb.Key('Collection','child1a')
    self.child2 = ndb.Key('Collection','child2')
    self.child2a = ndb.Key('Collection','child2a')

    global TestTagModel
    class TestTagModel(model.Taggable, model.AddCollection, ndb.Model):
      """This is a test class for trying out tags
      """
      name = ndb.StringProperty()


    #self.icon1 = model.IconStructure(data='i1')
    #self.icon2 = model.IconStructure(data='i2')
    #self.icon3 = model.IconStructure(data='i3')
    self.icon1 = 'i1'
    self.icon2 = 'i2'
    self.icon3 = 'i3'
    #self.tag1 = model.TagStructure(name='one', icon=self.icon1, color='red')
    #self.tag2 = model.TagStructure(name='Two', icon=self.icon2, color='green')
    #self.tag3 = model.TagStructure(name='Three', icon=self.icon3, color='blue')
    #self.tag4 = model.TagStructure(name='four')
    #self.tags1 = [self.tag1,self.tag2,self.tag3, self.tag4]
    # Create tags
    model.Tag.add(name='one', icon_data=self.icon1, color='red', auto_incr=False)
    model.Tag.add(name='Two', icon_data=self.icon2, color='green', auto_incr=False)
    model.Tag.add(name='three', icon_data=self.icon3, color='blue', auto_incr=False)

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
    tag_dbs = model.Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 1)
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 0)
    #model.TagRelation.print_list(rel_dbs)

    demo1.add_tags([self.tag2, self.tag3])
    # show tags
    tag_dbs = model.Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 3)
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 6)
    #model.TagRelation.print_list(rel_dbs)

    demo1.add_tags(self.tags1)
    # show tags
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs), 4)
    rel_dbs = model.TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 4*3)
    #model.TagRelation.print_list(rel_dbs)

  def test_add_tag_with_collection(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags([self.tag1])
    demo1.put()
    demo1a = TestTagModel(name='demo1a',collection=self.child1a)
    demo1a.add_tags([self.tag1])
    demo1a.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs), 2)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs), 0)

    demo1a.add_tags([self.tag2, self.tag3])
    # show tags
    tag_dbs = model.Tag.qry().fetch()
    self.assertEqual(len(tag_dbs), 6)
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 6*2)
    #model.TagRelation.print_list(rel_dbs)

  def test_add_to_much_tags(self):
    demo1 = TestTagModel(name='demo1')
    # create a long list of tags
    tags = []
    for i in range (0,50):
      tags.append(model.TagStructure(name=str(i)))
    with self.assertRaises(UserWarning):
      demo1.add_tags(tags)
    demo1.put()

  def test_remove_tags(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags(self.tags1)
    demo1.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)

    demo1.remove_tags([self.tag1,self.tag2])
    demo1.put()
    # show tags and relations
    tag_dbs = model.Tag.qry(count_greater=-10).fetch()
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(tag_dbs[-1].count,0)
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    self.assertEqual(len(rel_dbs), 2)
    #model.TagRelation.print_list(rel_dbs)

  def test_remove_tags_with_collection(self):
    demo1 = TestTagModel(name='demo1')
    demo1.add_tags(self.tags1)
    demo1.put()
    demo1a = TestTagModel(name='demo1a',collection=self.child1a)
    demo1a.add_tags(self.tags1)
    demo1a.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)

    demo1a.remove_tags([self.tag1,self.tag2])
    demo1a.put()
    # show tags and relations
    tag_dbs = model.Tag.qry(count_greater=-10).fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,2)
    self.assertEqual(tag_dbs[-1].count,0)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs), 3*4+2)

  def test_update_tags(self):
    demo1 = TestTagModel(name='demo1')
    demo1.update_tags(self.tags1)
    demo1.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(len(tag_dbs),4)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(rel_dbs[0].count,1)
    self.assertEqual(len(rel_dbs),4*3)
    # Add the same, nothing should happen.
    demo1.update_tags(self.tags1)
    demo1.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(len(tag_dbs),4)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(rel_dbs[0].count,1)
    self.assertEqual(len(rel_dbs),4*3)

    ## Remove tags
    demo1.update_tags([self.tag1,self.tag2])
    demo1.put()
    self.assertEqual(demo1.tags[0],'one')
    self.assertEqual(demo1.tags[1],'two')
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(tag_dbs[-1].count,1)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs),2*1)

    # Add and remove and change order
    demo1.update_tags([self.tag3,self.tag2])
    demo1.put()
    self.assertEqual(demo1.tags[0],'three')
    self.assertEqual(demo1.tags[1],'two')
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(tag_dbs[0].count,1)
    self.assertEqual(tag_dbs[-1].count,1)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(len(rel_dbs),2*1)

    # With collection
    demo1a = TestTagModel(name='demo1a', collection=self.child1a)
    demo1a.update_tags(self.tags1+[self.tag1])
    demo1a.put()
    # show tags and relations
    tag_dbs = model.Tag.qry().fetch()
    #model.Tag.print_list(tag_dbs)
    self.assertEqual(len(tag_dbs),8)
    rel_dbs = model.TagRelation.qry().fetch()
    #model.TagRelation.print_list(rel_dbs)
    self.assertEqual(rel_dbs[0].count,3)
    self.assertEqual(len(rel_dbs),2*4*3)


if __name__ == "__main__":
  unittest.main()
