import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
#sys.path.append('./')
#sys.path.append('./model')

#import logging
import unittest

from google.appengine.ext import ndb#, testbed


#from .icon import Iconize, IconStructure, Icon
#from counter import CountableLazy


class TestIcon(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    global config
    global model
    import config
    import model
    # Create a few icons
    #self.i1s_name = model.IconStructure()
    #self.i2s_type = model.IconStructure(filetype='pixel')
    #self.i3s_data = model.IconStructure(data="BLOB")
    self.i1s_name = "NAME"
    self.i2s_type = 'TYPE'
    self.i3s_data = "DATA"
    self.colg = model.Collection.top_key()
    self.col1 = ndb.Key('Collection','one')
    self.col2 = ndb.Key('Collection','two')
    self.col3 = ndb.Key('Collection','three')
    self.col1a = ndb.Key('Collection','one A')
    self.col2a = ndb.Key('Collection','two A')
    self.col3a = ndb.Key('Collection','three A')

  def test_init_icon(self):
    i1 = model.Icon(icon=self.i1s_name,name='i1s_name')
    i1.put()
    assert i1 is not None
    self.assertEqual(i1.name, 'i1s_name')
    self.assertEqual(i1.filetype, 'svg')
    self.assertEqual(i1.collection, self.colg)

  def test_init_with_type_data_and_collection(self):
    i2 = model.Icon(icon=self.i2s_type,name='i2s_type',filetype='pixel')
    i3 = model.Icon(icon=self.i3s_data,name='i3s_data',collection=self.col1)
    ndb.put_multi([i2,i3])
    self.assertEqual(i2.name, 'i2s_type')
    self.assertEqual(i2.filetype, 'pixel')
    self.assertEqual(i3.collection,self.col1)
    self.assertEqual(i3.icon, 'DATA')


  def test_init_counter(self):
    i1 = model.Icon(icon=self.i1s_name,name='i1s_name')
    self.assertEqual(i1.count, 0)
    i1.incr()
    i1.put()
    self.assertEqual(i1.count, 1)
    i1.decr()
    i1.put()
    self.assertEqual(i1.count, 0)

  #def test_post_put_get_icon(self):
    #i1 = model.Icon(icon=self.i1s_name,name='i')
    #i1.put()
    #i1sn = i1.get_icon()
    #self.assertEqual(i1sn.icon_key,ndb.Key('Icon', 1))

  #def test_pre_put_get_icon(self):
    #i1 = model.Icon(icon=self.i1s_name,name='i')
    #with self.assertRaises(UserWarning):
      #i1sn = i1.get_icon()
    #i1.put()
    #i1sn = i1.get_icon()
    #self.assertEqual(i1sn.icon_key,ndb.Key('Icon', 1))


  def test_init_icon_with_collection(self):
    i1 = model.Icon(icon=self.i1s_name,name='i1s_name', collection=self.col1)
    i1.put()
    assert i1 is not None
    self.assertEqual(i1.name, 'i1s_name')
    self.assertEqual(i1.collection, self.col1)

  def test_init_icon_toplevel_and_incr(self):
    top = model.Icon(icon=self.i1s_name,name='i' )
    top_key = top.put()
    one = model.Icon(icon=self.i1s_name,name='i',
        collection=self.col1,
        toplevel=top_key)
    two = model.Icon(icon=self.i1s_name,name='i',
        collection=self.col2,
        toplevel=top_key)
    two.put()
    self.assertEqual(top.count, 0)
    self.assertEqual(one.count, 0)
    self.assertEqual(two.count, 0)
    one.incr()
    one.put()
    self.assertEqual(top.count, 1)
    self.assertEqual(one.count, 1)
    self.assertEqual(two.count, 0)
    two.incr()
    two.put()
    self.assertEqual(top.count, 2)
    self.assertEqual(one.count, 1)
    self.assertEqual(two.count, 1)
    one.decr()
    one.put()
    self.assertEqual(top.count, 1)
    self.assertEqual(one.count, 0)
    self.assertEqual(two.count, 1)

  def test_add_one_icon(self):
    icon = model.Icon()
    icon.collection = self.col1
    icon.icon = self.i1s_name
    icon.name = 'i1s_name'
    icon_key = icon._add_and_put()
    assert icon.toplevel is not None

    #get new created toplevel
    top = icon.toplevel.get()
    self.assertEqual(top.name,'i1s_name')
    self.assertEqual(top.collection,self.colg)
    self.assertEqual(top.count,1)
    self.assertEqual(icon.count,1)
    self.assertEqual(icon.collection,self.col1)

    # Add the same again with different collection
    icon.collection = self.col1
    icon.icon = self.i1s_name
    icon_key = icon._add_and_put()
    #get new created toplevel
    top = icon.toplevel.get()
    self.assertEqual(top.count,2)
    self.assertEqual(icon.count,2)

  def test_add_multiple_icon_collections(self):
    icon = model.Icon()
    icon.collection = self.col1
    icon.name = 'i'
    icon.icon = self.i1s_name
    icon_key = icon._add_and_put()

    #get new created toplevel
    top = icon.toplevel.get()
    self.assertEqual(top.count,1)
    self.assertEqual(icon.count,1)

    icon2 = model.Icon()
    icon2.toplevel = icon.toplevel
    icon2.collection = self.col2
    icon2.name = 'i2'
    icon2.icon = icon.icon
    icon_key = icon2._add_and_put()
    #get new created toplevel
    top2 = icon2.toplevel.get()
    self.assertEqual(top2.count,2)
    self.assertEqual(icon2.count,1)
    self.assertEqual(icon.count,1)

  def test_create_icon(self):
    """Test creates new icon.
    1. A 'global' icon
    2. Two children
    3. A 'children' icon without a topevel icon
    """
    key = model.Icon.create(icon=self.i1s_name,name='i')
    icon_db = key.get()
    self.assertEqual(icon_db.key , key)
    self.assertEqual(icon_db.collection , self.colg)
    self.assertEqual(getattr(icon_db,'toplevel',None) , None)
    # create the same with collection
    key2 = model.Icon.create(icon=self.i1s_name,name='i',
        collection=self.col1,
        toplevel=key)
    icon2_db = key2.get()
    self.assertEqual(icon2_db.key , key2)
    self.assertEqual(icon2_db.collection , self.col1)
    self.assertEqual(icon2_db.count,1)
    key3 = model.Icon.create(icon=self.i1s_name,name='i',
        collection=self.col2,
        toplevel=key)
    icon_db = key.get()
    self.assertEqual(icon_db.count,3)
    # auto=False, no  new toplevel
    key4 = model.Icon.create(icon=self.i1s_name,name='i',
        collection=self.col2,
        auto = False)
    icon4_db = key.get()
    self.assertEqual(icon4_db.count,3)
    self.assertEqual(icon4_db.toplevel,None)

  def test_add_icon(self):
    """ Test for adding icons """
    # Create global icon
    key = model.Icon.create(icon=self.i1s_name,name='i')
    # Add a second
    model.Icon.add(key)
    icon_db = key.get()
    self.assertEqual(icon_db.count,2)
    self.assertEqual(icon_db.collection , self.colg)
    # Add a thrid but with collection
    # should increase 'global' counter and create a new child with
    # this collection
    key2 = model.Icon.add(key,collection=self.col1)
    icon_db = key.get()
    icon2_db = key2.get()
    self.assertEqual(icon_db.count,3)
    self.assertEqual(icon2_db.count,1)
    self.assertEqual(icon2_db.collection,self.col1)
    # add the same again, not new icon should be created
    key3 = model.Icon.add(key,collection=self.col1)
    self.assertEqual(key2,key3)
    icon2_db = key2.get()
    self.assertEqual(icon2_db.count,2)
    # and a third time the same
    key4 = model.Icon.add(key,collection=self.col1)
    self.assertEqual(key2,key4)
    icon2_db = key2.get()
    icon_db = key.get()
    self.assertEqual(icon_db.count,5)
    self.assertEqual(icon2_db.count,3)
    ######
    # Test the same but with 'test1' as key
    # A "neighbour" icon should be added
    keyA = model.Icon.add(key2,collection=self.col2)
    icon_db = key.get()
    icon2_db = key2.get()
    iconA_db = keyA.get()
    self.assertEqual(icon_db.count,6)
    self.assertEqual(iconA_db.count,1)
    self.assertEqual(iconA_db.collection,self.col2)
    self.assertEqual(iconA_db.toplevel,key)
    self.assertEqual(icon2_db.count,3)
    ######
    # Test the same but with 'test1a' as toplevel key
    # A "children" icon should be added
    key2a = model.Icon.add(key2,collection=self.col1a,as_child=True)
    icon_db = key.get()
    icon2_db = key2.get()
    icon2a_db = key2a.get()
    self.assertEqual(icon_db.count,7)
    self.assertEqual(icon2a_db.count,1)
    self.assertEqual(icon2a_db.collection,self.col1a)
    self.assertEqual(icon2a_db.toplevel,key2)
    self.assertEqual(icon2_db.count,4)

  def test_remove_icon(self):
    """ Test for adding icons """
    # Create global icon
    key = model.Icon.create(icon=self.i1s_name,name='i')
    # Add a second
    model.Icon.add(key)
    icon_db = key.get()
    self.assertEqual(icon_db.count,2)
    ## Remove it
    model.Icon.remove(key.id())
    icon_db = key.get()
    self.assertEqual(icon_db.count,1)
    ## Add icon with collection and remove it
    key2 = model.Icon.add(key,collection=self.col1)
    model.Icon.remove(key2.id())
    icon_db = key.get()
    icon2_db = key2.get()
    self.assertEqual(icon_db.count,1)
    self.assertEqual(icon2_db.count,0)

  def test_get_icon_by_toplevel(self):
    key = model.Icon.create(icon=self.i1s_name,name='i')
    for i in range(0,10):
      key2 = model.Icon.add(key,collection=self.col2)
      key3 = model.Icon.add(key,collection=self.col3)
      key3a = model.Icon.add(key3,collection=self.col3a,as_child=True)
      key10 = model.Icon.add(key,collection=ndb.Key('Collection','test{}'.format(i+10)))
    icon_db = key.get()
    icon2_db = key2.get()
    icon3_db = key3.get()
    icon3a_db = key3a.get()
    self.assertEqual(icon_db.count,41)
    self.assertEqual(icon2_db.count,10)
    self.assertEqual(icon3_db.count,20)
    self.assertEqual(icon3a_db.count,10)
    dbs = model.Icon.get_by_toplevel(key)
    self.assertEqual(len(dbs),12)
    ## check order
    self.assertTrue(dbs[0].cnt > dbs[-1].cnt)
    # get all toplevel
    # create a new global key
    keyNew = model.Icon.create(icon=self.i1s_name,name='i')
    top_dbs = model.Icon.get_by_toplevel(collection=self.colg)
    self.assertEqual(len(top_dbs),2)
    # test with collections
    test2_dbs = model.Icon.get_by_toplevel(key,collection=self.col2)
    test12_dbs = model.Icon.get_by_toplevel(key,collection=ndb.Key('Collection','test12'))
    self.assertEqual(len(test2_dbs),1)
    self.assertEqual(len(test12_dbs),1)

  def test_icon_query(self):
    key = model.Icon.create(icon=self.i1s_name,name='i')
    for i in range(0,10):
      key2 = model.Icon.add(key,collection=self.col2)
      key3 = model.Icon.add(key,collection=self.col3)
      key3a = model.Icon.add(key3,collection=self.col3a,as_child=True)
      key10 = model.Icon.add(key,collection=ndb.Key('Collection','test{}'.format(i+10)))
    keyA = model.Icon.create(icon=self.i1s_name,name='i',private=True)
    keyB = model.Icon.create(icon=self.i1s_name,name='i2')
    icon_db = key.get()
    icon2_db = key2.get()
    icon3_db = key3.get()
    icon3a_db = key3a.get()
    self.assertEqual(len(model.Icon.qry().fetch()),15)
    self.assertEqual(len(model.Icon.qry(private=True).fetch()),16)
    self.assertEqual(len(model.Icon.qry(key3).fetch()),1)
    self.assertEqual(len(model.Icon.qry(key).fetch()),12)
    self.assertEqual(len(model.Icon.qry(name='i',private=True).fetch()),15)



class TestIconizedModel(unittest.TestCase):

  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    global config
    global model
    import config
    import model

    global TestIconModel
    class TestIconModel(model.Iconize, model.AddCollection, ndb.Model):
      """This is a test class for trying out icons
      """
      name = ndb.StringProperty()
      #collection = ndb.StringProperty()




    # Create a few icons
    #self.i1s_name = model.IconStructure()
    #self.i2s_type = model.IconStructure(filetype='pixel')
    #self.i3s_data = model.IconStructure(data="BLOB")
    self.i1s_name = "NAME"
    self.i2s_type = 'TYPE'
    self.i3s_data = "DATA"
    self.colg = model.Collection.top_key()
    self.col1 = ndb.Key('Collection','one')
    self.col2 = ndb.Key('Collection','two')
    self.col3 = ndb.Key('Collection','three')
    self.col1a = ndb.Key('Collection','one A')
    self.col2a = ndb.Key('Collection','two A')
    self.col3a = ndb.Key('Collection','three A')

  def tearDown(self):
    pass


  def test_iconized_init(self):
    im = TestIconModel(name="X")
    im.create_icon(self.i1s_name,name='1')
    key1 = im.put()
    im_db = key1.get()
    assert im_db.icon_id is not None
    im2 = TestIconModel(name="X2")
    im2.add_icon(id=im_db.icon_id)
    key2 = im2.put()
    im2_db = key2.get()
    assert im2_db.icon_id is not None
    icon_dbs = model.Icon.qry().fetch()
    self.assertEqual(len(icon_dbs),1)
    self.assertEqual(icon_dbs[0].collection,self.colg)
    self.assertEqual(icon_dbs[0].cnt,2)
    self.assertEqual(icon_dbs[0].key.id(),im2_db.icon_id)

  def test_iconized_with_collection(self):
    im = TestIconModel(name="X",collection=self.col1)
    im.create_icon(self.i1s_name,name='1')
    key1 = im.put()
    im_db = key1.get()
    assert im_db.icon_id is not None
    icon_dbs = model.Icon.qry().fetch()
    self.assertEqual(len(icon_dbs),2)
    icon_dbs = model.Icon.qry(collection=self.col1).fetch()
    self.assertEqual(len(icon_dbs),1)
    self.assertEqual(icon_dbs[0].collection,self.col1)
    self.assertEqual(icon_dbs[0].cnt,1)
    self.assertEqual(icon_dbs[0].key.id(),im_db.icon_id)

  def test_iconized_remove_icon(self):
    im = TestIconModel(name="X",collection=self.col1)
    im.create_icon(self.i1s_name,name='1')
    key1 = im.put()
    im_db = key1.get()
    assert im_db.icon_id is not None
    im.remove_icon()
    key1 = im.put()
    im_db = key1.get()
    self.assertEqual(im_db.icon_id,0)
    icon_db = model.Icon.qry().get()
    self.assertEqual(icon_db.cnt,0)


if __name__ == "__main__":
  unittest.main()
