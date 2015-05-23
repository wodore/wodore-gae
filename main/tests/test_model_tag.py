import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
sys.path.append('./')
sys.path.append('./model')

#import logging
import unittest

from google.appengine.ext import ndb#, testbed


from tag import Taggable, IconStructure, Tag
#from counter import CountableLazy


class TestTag(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    pass
    # Create a few icons
    #self.i1s_name = IconStructure()
    #self.i2s_type = IconStructure(filetype='png')
    #self.i3s_data = IconStructure(data="BLOB")

  def test_init_icon(self):
    tag1 = Tag(name='tag1')
    tag1.put()
    assert tag1 is not None
    self.assertEqual(tag1.name, 'tag1')
    #self.assertEqual(i1.icon.filetype, 'svg')
    #self.assertEqual(i1.collection, 'global')
#
#  def test_init_with_type_data_and_collection(self):
#    i2 = Icon(icon=self.i2s_type,name='i2s_type')
#    i3 = Icon(icon=self.i3s_data,name='i3s_data',collection='one')
#    ndb.put_multi([i2,i3])
#    self.assertEqual(i2.name, 'i2s_type')
#    self.assertEqual(i2.icon.filetype, 'png')
#    self.assertEqual(i3.collection, 'one')
#    self.assertEqual(i3.icon.data, 'BLOB')
#
#
#  def test_init_counter(self):
#    i1 = Icon(icon=self.i1s_name,name='i1s_name')
#    self.assertEqual(i1.count, 0)
#    i1.incr()
#    i1.put()
#    self.assertEqual(i1.count, 1)
#    i1.decr()
#    i1.put()
#    self.assertEqual(i1.count, 0)
#
#  def test_post_put_get_icon(self):
#    i1 = Icon(icon=self.i1s_name,name='i')
#    i1.put()
#    i1sn = i1.get_icon()
#    self.assertEqual(i1sn.icon_key,ndb.Key('Icon', 1))
#
#  def test_pre_put_get_icon(self):
#    i1 = Icon(icon=self.i1s_name,name='i')
#    with self.assertRaises(UserWarning):
#      i1sn = i1.get_icon()
#    i1.put()
#    i1sn = i1.get_icon()
#    self.assertEqual(i1sn.icon_key,ndb.Key('Icon', 1))
#
#
#  def test_init_icon_with_collection(self):
#    i1 = Icon(icon=self.i1s_name,name='i1s_name', collection='one')
#    i1.put()
#    assert i1 is not None
#    self.assertEqual(i1.name, 'i1s_name')
#    self.assertEqual(i1.collection, 'one')
#
#  def test_init_icon_toplevel_and_incr(self):
#    top = Icon(icon=self.i1s_name,name='i' )
#    top_key = top.put()
#    one = Icon(icon=self.i1s_name,name='i',
#        collection='one',
#        toplevel=top_key)
#    two = Icon(icon=self.i1s_name,name='i',
#        collection='two',
#        toplevel=top_key)
#    two.put()
#    self.assertEqual(top.count, 0)
#    self.assertEqual(one.count, 0)
#    self.assertEqual(two.count, 0)
#    one.incr()
#    one.put()
#    self.assertEqual(top.count, 1)
#    self.assertEqual(one.count, 1)
#    self.assertEqual(two.count, 0)
#    two.incr()
#    two.put()
#    self.assertEqual(top.count, 2)
#    self.assertEqual(one.count, 1)
#    self.assertEqual(two.count, 1)
#    one.decr()
#    one.put()
#    self.assertEqual(top.count, 1)
#    self.assertEqual(one.count, 0)
#    self.assertEqual(two.count, 1)
#
#  def test_add_one_icon(self):
#    icon = Icon()
#    icon.collection = 'one'
#    icon.icon = self.i1s_name
#    icon.name = 'i1s_name'
#    icon_key = icon._add_and_put()
#    assert icon.toplevel is not None
#
#    #get new created toplevel
#    top = icon.toplevel.get()
#    self.assertEqual(top.name,'i1s_name')
#    self.assertEqual(top.collection,'global')
#    self.assertEqual(top.count,1)
#    self.assertEqual(icon.count,1)
#    self.assertEqual(icon.collection,'one')
#
#    # Add the same again with different collection
#    icon.collection = 'one'
#    icon.icon = self.i1s_name
#    icon_key = icon._add_and_put()
#    #get new created toplevel
#    top = icon.toplevel.get()
#    self.assertEqual(top.count,2)
#    self.assertEqual(icon.count,2)
#
#  def test_add_multiple_icon_collections(self):
#    icon = Icon()
#    icon.collection = 'one'
#    icon.name = 'i'
#    icon.icon = self.i1s_name
#    icon_key = icon._add_and_put()
#
#    #get new created toplevel
#    top = icon.toplevel.get()
#    self.assertEqual(top.count,1)
#    self.assertEqual(icon.count,1)
#
#    icon2 = Icon()
#    icon2.toplevel = icon.toplevel
#    icon2.collection = 'two'
#    icon2.name = 'i2'
#    icon2.icon = icon.icon
#    icon_key = icon2._add_and_put()
#    #get new created toplevel
#    top2 = icon2.toplevel.get()
#    self.assertEqual(top2.count,2)
#    self.assertEqual(icon2.count,1)
#    self.assertEqual(icon.count,1)
#
#  def test_create_icon(self):
#    """Test creates new icon.
#    1. A 'global' icon
#    2. Two children
#    3. A 'children' icon without a topevel icon
#    """
#    key = Icon.create(icon=self.i1s_name,name='i')
#    icon_db = key.get()
#    self.assertEqual(icon_db.key , key)
#    self.assertEqual(icon_db.icon.icon_key , key)
#    self.assertEqual(icon_db.collection , 'global')
#    self.assertEqual(getattr(icon_db,'toplevel',None) , None)
#    # create the same with collection
#    key2 = Icon.create(icon=self.i1s_name,name='i',
#        collection='one_cat',
#        toplevel=key)
#    icon2_db = key2.get()
#    self.assertEqual(icon2_db.icon.icon_key , key2)
#    self.assertEqual(icon2_db.collection , 'one_cat')
#    self.assertEqual(icon2_db.count,1)
#    key3 = Icon.create(icon=self.i1s_name,name='i',
#        collection='two_cat',
#        toplevel=key)
#    icon_db = key.get()
#    self.assertEqual(icon_db.count,3)
#    # auto=False, no  new toplevel
#    key4 = Icon.create(icon=self.i1s_name,name='i',
#        collection='two_cat',
#        auto = False)
#    icon4_db = key.get()
#    self.assertEqual(icon4_db.count,3)
#    self.assertEqual(icon4_db.toplevel,None)
#
#  def test_add_icon(self):
#    """ Test for adding icons """
#    # Create global icon
#    key = Icon.create(icon=self.i1s_name,name='i')
#    # Add a second
#    Icon.add(key)
#    icon_db = key.get()
#    self.assertEqual(icon_db.count,2)
#    self.assertEqual(icon_db.collection , 'global')
#    # Add a thrid but with collection
#    # should increase 'global' counter and create a new child with
#    # this collection
#    key2 = Icon.add(key,collection='test1')
#    icon_db = key.get()
#    icon2_db = key2.get()
#    self.assertEqual(icon_db.count,3)
#    self.assertEqual(icon2_db.count,1)
#    self.assertEqual(icon2_db.collection,'test1')
#    # add the same again, not new icon should be created
#    key3 = Icon.add(key,collection='test1')
#    self.assertEqual(key2,key3)
#    icon2_db = key2.get()
#    self.assertEqual(icon2_db.count,2)
#    # and a third time the same
#    key4 = Icon.add(key,collection='test1')
#    self.assertEqual(key2,key4)
#    icon2_db = key2.get()
#    icon_db = key.get()
#    self.assertEqual(icon_db.count,5)
#    self.assertEqual(icon2_db.count,3)
#    ######
#    # Test the same but with 'test1' as key
#    # A "neighbour" icon should be added
#    keyA = Icon.add(key2,collection='test2')
#    icon_db = key.get()
#    icon2_db = key2.get()
#    iconA_db = keyA.get()
#    self.assertEqual(icon_db.count,6)
#    self.assertEqual(iconA_db.count,1)
#    self.assertEqual(iconA_db.collection,'test2')
#    self.assertEqual(iconA_db.toplevel,key)
#    self.assertEqual(icon2_db.count,3)
#    ######
#    # Test the same but with 'test1a' as toplevel key
#    # A "children" icon should be added
#    key2a = Icon.add(key2,collection='test1a',as_child=True)
#    icon_db = key.get()
#    icon2_db = key2.get()
#    icon2a_db = key2a.get()
#    self.assertEqual(icon_db.count,7)
#    self.assertEqual(icon2a_db.count,1)
#    self.assertEqual(icon2a_db.collection,'test1a')
#    self.assertEqual(icon2a_db.toplevel,key2)
#    self.assertEqual(icon2_db.count,4)
#
#  def test_remove_icon(self):
#    """ Test for adding icons """
#    # Create global icon
#    key = Icon.create(icon=self.i1s_name,name='i')
#    # Add a second
#    Icon.add(key)
#    icon_db = key.get()
#    self.assertEqual(icon_db.count,2)
#    ## Remove it
#    Icon.remove(key)
#    icon_db = key.get()
#    self.assertEqual(icon_db.count,1)
#    ## Add icon with collection and remove it
#    key2 = Icon.add(key,collection='test1')
#    Icon.remove(key2)
#    icon_db = key.get()
#    icon2_db = key2.get()
#    self.assertEqual(icon_db.count,1)
#    self.assertEqual(icon2_db.count,0)
#
#  def test_get_icon_by_toplevel(self):
#    key = Icon.create(icon=self.i1s_name,name='i')
#    for i in range(0,10):
#      key2 = Icon.add(key,collection='test2')
#      key3 = Icon.add(key,collection='test3')
#      key3a = Icon.add(key3,collection='test3a',as_child=True)
#      key10 = Icon.add(key,collection='test{}'.format(i+10))
#    icon_db = key.get()
#    icon2_db = key2.get()
#    icon3_db = key3.get()
#    icon3a_db = key3a.get()
#    self.assertEqual(icon_db.count,41)
#    self.assertEqual(icon2_db.count,10)
#    self.assertEqual(icon3_db.count,20)
#    self.assertEqual(icon3a_db.count,10)
#    dbs = Icon.get_by_toplevel(key)
#    self.assertEqual(len(dbs),12)
#    ## check order
#    self.assertTrue(dbs[0].cnt > dbs[-1].cnt)
#    # get all toplevel
#    # create a new global key
#    keyNew = Icon.create(icon=self.i1s_name,name='i')
#    top_dbs = Icon.get_by_toplevel(collection='global')
#    self.assertEqual(len(top_dbs),2)
#    # test with collections
#    test2_dbs = Icon.get_by_toplevel(key,collection='test2')
#    test12_dbs = Icon.get_by_toplevel(key,collection='test12')
#    self.assertEqual(len(test2_dbs),1)
#    self.assertEqual(len(test12_dbs),1)
#
#  def test_icon_query(self):
#    key = Icon.create(icon=self.i1s_name,name='i')
#    for i in range(0,10):
#      key2 = Icon.add(key,collection='test2')
#      key3 = Icon.add(key,collection='test3')
#      key3a = Icon.add(key3,collection='test3a',as_child=True)
#      key10 = Icon.add(key,collection='test{}'.format(i+10))
#    keyA = Icon.create(icon=self.i1s_name,name='i',private=True)
#    keyB = Icon.create(icon=self.i1s_name,name='i2')
#    icon_db = key.get()
#    icon2_db = key2.get()
#    icon3_db = key3.get()
#    icon3a_db = key3a.get()
#    self.assertEqual(len(Icon.qry().fetch()),15)
#    self.assertEqual(len(Icon.qry(private=True).fetch()),16)
#    self.assertEqual(len(Icon.qry(key3).fetch()),1)
#    self.assertEqual(len(Icon.qry(key).fetch()),12)
#    self.assertEqual(len(Icon.qry(name='i',private=True).fetch()),15)
#
#
#class TestIconModel(Iconize, ndb.Model):
#  """This is a test class for trying out tags
#  """
#  name = ndb.StringProperty()
#  collection = ndb.StringProperty()
#
#
#class TestIconizedModel(unittest.TestCase):
#
#  # enable the datastore stub
#  nosegae_datastore_v3 = True
#  nosegae_memcache = True
#
#  def setUp(self):
#    # Create a few icons
#    self.i1s_name = IconStructure()
#    self.i2s_type = IconStructure(filetype='png')
#    self.i3s_data = IconStructure(data="BLOB")
#
#  def tearDown(self):
#    pass
#
#
#  def test_iconized_init(self):
#    im = TestIconModel(name="X")
#    im.create_icon(self.i1s_name,name='1')
#    key1 = im.put()
#    im_db = key1.get()
#    assert im_db.icon is not None
#    im2 = TestIconModel(name="X2")
#    im2.add_icon(im_db.icon.icon_key)
#    key2 = im2.put()
#    im2_db = key2.get()
#    assert im2_db.icon is not None
#    icon_dbs = Icon.qry().fetch()
#    self.assertEqual(len(icon_dbs),1)
#    self.assertEqual(icon_dbs[0].collection,'global')
#    self.assertEqual(icon_dbs[0].cnt,2)
#    self.assertEqual(icon_dbs[0].icon,im2_db.icon)
#
#  def test_iconized_with_collection(self):
#    im = TestIconModel(name="X",collection='one')
#    im.create_icon(self.i1s_name,name='1')
#    key1 = im.put()
#    im_db = key1.get()
#    assert im_db.icon is not None
#    icon_dbs = Icon.qry().fetch()
#    self.assertEqual(len(icon_dbs),2)
#    icon_dbs = Icon.qry(collection='one').fetch()
#    self.assertEqual(len(icon_dbs),1)
#    self.assertEqual(icon_dbs[0].collection,'one')
#    self.assertEqual(icon_dbs[0].cnt,1)
#    self.assertEqual(icon_dbs[0].icon,im_db.icon)
#
#  def test_iconized_remove_icon(self):
#    im = TestIconModel(name="X",collection='one')
#    im.create_icon(self.i1s_name,name='1')
#    key1 = im.put()
#    im_db = key1.get()
#    assert im_db.icon is not None
#    im.remove_icon()
#    key1 = im.put()
#    im_db = key1.get()
#    assert im_db.icon is None
#    icon_db = Icon.qry().get()
#    self.assertEqual(icon_db.cnt,0)
#

if __name__ == "__main__":
  unittest.main()
