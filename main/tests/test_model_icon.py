import sys
#sys.path.append('/home/tobias/data/git/wodore-gae/main/')
sys.path.append('./')
sys.path.append('./model')

#import logging
import unittest

from google.appengine.ext import ndb#, testbed


from icon import Iconize, IconStructure, Icon
#from counter import CountableLazy


class TestIcon(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    # Create a few icons
    self.i1s_name = IconStructure(name='i1s_name')
    self.i2s_type = IconStructure(name='i2s_type', filetype='png')
    self.i3s_data = IconStructure(name='i3s_data',data="BLOB")

  def test_init_icon(self):
    i1 = Icon(icon=self.i1s_name)
    i1.put()
    assert i1 is not None
    self.assertEqual(i1.icon.name, 'i1s_name')
    self.assertEqual(i1.icon.filetype, 'svg')
    self.assertEqual(i1.collection, 'global')

  def test_init_with_type_data_and_collection(self):
    i2 = Icon(icon=self.i2s_type)
    i3 = Icon(icon=self.i3s_data,collection='one')
    ndb.put_multi([i2,i3])
    self.assertEqual(i2.icon.name, 'i2s_type')
    self.assertEqual(i2.icon.filetype, 'png')
    self.assertEqual(i3.collection, 'one')
    self.assertEqual(i3.icon.data, 'BLOB')


  def test_init_counter(self):
    i1 = Icon(icon=self.i1s_name)
    self.assertEqual(i1.count, 0)
    i1.incr()
    i1.put()
    self.assertEqual(i1.count, 1)
    i1.decr()
    i1.put()
    self.assertEqual(i1.count, 0)

  def test_post_put_get_icon(self):
    i1 = Icon(icon=self.i1s_name)
    i1.put()
    i1sn = i1.get_icon()
    self.assertEqual(i1sn.icon_key,ndb.Key('Icon', 1))

  def test_pre_put_get_icon(self):
    i1 = Icon(icon=self.i1s_name)
    with self.assertRaises(UserWarning):
      i1sn = i1.get_icon()
    i1.put()
    i1sn = i1.get_icon()
    self.assertEqual(i1sn.icon_key,ndb.Key('Icon', 1))


  def test_init_icon_with_collection(self):
    i1 = Icon(icon=self.i1s_name, collection='one')
    i1.put()
    assert i1 is not None
    self.assertEqual(i1.icon.name, 'i1s_name')
    self.assertEqual(i1.collection, 'one')

  def test_init_icon_toplevel_and_incr(self):
    top = Icon(icon=self.i1s_name )
    top_key = top.put()
    one = Icon(icon=self.i1s_name,
        collection='one',
        toplevel=top_key)
    two = Icon(icon=self.i1s_name,
        collection='two',
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
    icon = Icon()
    print "Icon pre add and put: {}".format(icon)
    icon_key = icon.add_and_put(self.i1s_name,'one')
    assert icon.toplevel is not None
    print "Icon post add and put: {}".format(icon)
    #print "Icon toplevel: {}".format(icon.icon.toplevel)
    print "Icon key: {}".format(icon_key)

    #get new created toplevel
    top = icon.toplevel.get()
    print "Top icon: {}".format(top)
    self.assertEqual(top.icon.name,'i1s_name')
    self.assertEqual(top.collection,'global')
    self.assertEqual(top.count,1)
    self.assertEqual(icon.count,1)
    self.assertEqual(icon.collection,'one')

    # Add the same again with different collection
    icon_key = icon.add_and_put(self.i1s_name,'one')
    #get new created toplevel
    top = icon.toplevel.get()
    self.assertEqual(top.count,2)
    self.assertEqual(icon.count,2)

  def test_add_multiple_icon_collections(self):
    icon = Icon()
    icon_key = icon.add_and_put(self.i1s_name,'one')

    #get new created toplevel
    top = icon.toplevel.get()
    self.assertEqual(top.count,1)
    self.assertEqual(icon.count,1)

    print "Parameter icon: {}".format(icon)
    print "Parameter top: {}".format(top)
    icon2 = Icon()
    icon2.toplevel = icon.toplevel
    icon_key = icon2.add_and_put(icon.icon,'two')
    print "Parameter icon2: {}".format(icon2)
    #get new created toplevel
    top2 = icon2.toplevel.get()
    self.assertEqual(top2.count,2)
    self.assertEqual(icon2.count,1)
    self.assertEqual(icon.count,1)
    print "Parameter top2: {}".format(top)






#class TestIconModel(Iconize, ndb.Model):
#  """This is a test class for trying out tags
#  """
#  name = ndb.StringProperty()
#
#
#class TestTags(unittest.TestCase):
#
#  # enable the datastore stub
#  nosegae_datastore_v3 = True
#  nosegae_memcache = True
#
#  def setUp(self):
#    pass
#
#  def tearDown(self):
#    pass
#
#
#  def test_init(self):
#    im = TestIconModel(name="X")
#    im.put()
#    assert im is not None
#    self.assertEqual(im.icon, None)
#
#  def test_add_icon(self):
#    im = TestIconModel(name="X")
#    im.put()
#    test_icon = IconStructure(name="icon",filetype="svg")
#    im.icon = test_icon
#    im.put()
#    self.assertEqual(im.icon, test_icon)
#    self.assertEqual(im.icon.name, "icon")
#

if __name__ == "__main__":
  unittest.main()
