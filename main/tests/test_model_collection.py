import sys, os

#import logging
import unittest

from google.appengine.ext import ndb #, testbed
from google.appengine.api import datastore_errors

class TestCollection(unittest.TestCase):
  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True
  #import model # does not work yet

  def setUp(self):
    global config
    global model
    import config
    import model
    # add some user to user db
    self.user = []
    self.user.append(model.User(key=ndb.Key('User','zero'),
        name = 'User Zero', username='zero',
        email = 'zero@test.com', active = False, verified = False))
    self.user.append(model.User(key=ndb.Key('User','one'),
        name = 'User One', username='one',
        email = 'one@test.com', active = True, verified = True))
    self.user.append(model.User(key=ndb.Key('User','two'),
        name = 'User Two', username='two',
        email = 'two@test.com', active = True, verified = True))
    self.user.append(model.User(key=ndb.Key('User','three'),
        name = 'User Three', username='three',
        email = 'three@test.com', active = True, verified = True))
    self.user_key = []
    for u in self.user:
      self.user_key.append(u.put())

  def test_init_collection(self):
    C1 = model.Collection(name='C1')
    C1.put()
    assert C1 is not None
    self.assertEqual(C1.name, 'C1')

  def test_create_collection(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    db = key1.get()
    #model.Collection.print_list([db])
    self.assertEqual(db.name, 'C1')
    self.assertTrue(db.active)
    self.assertFalse(db.public)
    self.assertEqual(db.creator, ndb.Key('User','one'))
    self.assertEqual(db.cnt, 1)
    db.incr()
    db.put()
    db = key1.get()
    self.assertEqual(db.cnt, 2)

  def test_query_collection(self):
    model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.create(name='C2',creator=ndb.Key('User','one'))
    model.Collection.create(name='C3',creator=ndb.Key('User','two'),public=True)
    model.Collection.create(name='C4',creator=ndb.Key('User','two'))
    model.Collection.create(name='C4',creator=ndb.Key('User','three'),private=True)
    model.Collection.create(name='C4',creator=ndb.Key('User','three'),active=False)
    dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(dbs)
    self.assertEqual(len(dbs), 5)
    dbs = model.Collection.qry(name='C1').fetch()
    #model.Collection.print_list(dbs)
    self.assertEqual(len(dbs), 1)
    dbs = model.Collection.qry(active=False).fetch()
    #model.Collection.print_list(dbs)
    self.assertEqual(len(dbs), 1)
    dbs = model.Collection.qry(public=True).fetch()
    #model.Collection.print_list(dbs)
    self.assertEqual(len(dbs), 1)
    dbs = model.Collection.qry(private=True).fetch()
    #model.Collection.print_list(dbs)
    self.assertEqual(len(dbs), 1)
    dbs = model.Collection.qry(creator=ndb.Key('User','two')).fetch()
    #model.Collection.print_list(dbs)
    self.assertEqual(len(dbs), 2)

  def test_add_users_to_collection(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.add_users(key1,[ndb.Key('User','three'),
      ndb.Key('User','two'),ndb.Key('User','one')])
    col_dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(col_dbs)
    self.assertEqual(len(col_dbs), 1)
    self.assertEqual(col_dbs[0].count, 3)

    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 3)
    self.assertEqual(usr_dbs[0].collection, key1)
    self.assertEqual(usr_dbs[0].key.parent(), key1)

  def test_add_same_users_to_collection(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.add_users(key1,[ndb.Key('User','three'),ndb.Key('User','three'),
      ndb.Key('User','two'),ndb.Key('User','one'),ndb.Key('User','one'),\
          ndb.Key('User','three')])
    col_dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(col_dbs)
    self.assertEqual(len(col_dbs), 1)
    self.assertEqual(col_dbs[0].count, 3)

    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 3)

  def test_add_users_to_collection_with_diff_permission(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.add_users(key1,[[ndb.Key('User','three'),'read'],
      [ndb.Key('User','two'),'write'],[ndb.Key('User','one'),'none']],
      permission=False)
    col_dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(col_dbs)
    self.assertEqual(len(col_dbs), 1)
    self.assertEqual(col_dbs[0].count, 3)

    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 3)
    self.assertEqual(usr_dbs[0].permission, 'write')
    self.assertEqual(usr_dbs[1].permission, 'read')
    self.assertEqual(usr_dbs[2].permission, 'creator') # creator is not ovewritten
                                          # it is last because it was not modified

  def test_remove_users_from_collection(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.add_users(key1,[[ndb.Key('User','three'),'read'],
      [ndb.Key('User','two'),'write'],[ndb.Key('User','one'),'none']],
      permission=False)
    col_dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(col_dbs)

    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 3)

# delete users with one none existing user
    model.Collection.remove_users(key1,[ndb.Key('User','two'),\
        ndb.Key('User','one'), ndb.Key('User','none')])

    col_dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(col_dbs)
    self.assertEqual(col_dbs[0].count, 1)


    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 1)

  def test__users_collection_permission(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.add_users(key1,[[ndb.Key('User','three'),'read'],
      [ndb.Key('User','two'),'write'],[ndb.Key('User','one'),'none']],
      permission=False)
    col_dbs = model.Collection.qry().fetch()
    #model.Collection.print_list(col_dbs)
    perm = model.Collection.has_permission(key1,ndb.Key('User','three'),'write')
    self.assertFalse(perm)
    perm = model.Collection.has_permission(key1,ndb.Key('User','three'),'read')
    self.assertTrue(perm)
    perm = model.Collection.has_permission(key1,ndb.Key('User','three'),'none')
    self.assertTrue(perm)
    perm = model.Collection.has_permission(key1,ndb.Key('User','three'),'none',True)
    self.assertFalse(perm)
    # see if permission is given back if the permission arg is ommited
    perm = model.Collection.has_permission(key1,ndb.Key('User','three'))
    self.assertEqual(perm, 'read')


  def test_update_collection_user(self):
    key1 = model.Collection.create(name='C1',creator=ndb.Key('User','one'))
    model.Collection.add_users(key1,[ndb.Key('User','three'),ndb.Key('User','three'),
      ndb.Key('User','two'),ndb.Key('User','one'),ndb.Key('User','one'),\
          ndb.Key('User','three')])
    key2 = model.Collection.create(name='C2',creator=ndb.Key('User','one'))
    model.Collection.add_users(key2,[ndb.Key('User','three'),ndb.Key('User','one')])
    key3 = model.Collection.create(name='C2',creator=ndb.Key('User','three'))
    model.Collection.add_users(key3,[ndb.Key('User','one')])

    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 7)

    one_db = ndb.Key('User','one').get()
    one_db.name = "New User One"
    ukey1 = one_db.put()
    model.CollectionUser.update_user(ukey1)

    usr_dbs = model.CollectionUser.qry().fetch()
    #model.CollectionUser.print_list(usr_dbs)
    self.assertEqual(len(usr_dbs), 7)
    self.assertEqual(usr_dbs[0].user_name, "New User One")
    self.assertEqual(usr_dbs[2].user_name, "New User One")




class TestAddCollectiondModel(unittest.TestCase):

  # enable the datastore stub
  nosegae_datastore_v3 = True
  nosegae_memcache = True

  def setUp(self):
    global config
    global model
    import config
    import model

    global TestCollectionModel
    class TestCollectionModel(model.AddCollection, ndb.Model):
      """This is a test class for with added collection
      """
      name = ndb.StringProperty()


  def tearDown(self):
    pass


  def test_add_collection_init(self):
    col1 = TestCollectionModel(name="X")
    key1 = col1.put()
    col1_db = key1.get()
    assert col1_db.collection is not None
    self.assertEqual(col1_db.collection,model.Collection.top_key())
    self.assertEqual(col1_db.collection.id(),model.Collection.top_keyname())

    col2 = TestCollectionModel(name="Y")
    with self.assertRaises(datastore_errors.BadValueError):
      col2.collection = 'NotAKey'
      key2 = col2.put()
    col2.collection = ndb.Key('Collection','Key')
    key2 = col2.put()
    col2_db = key2.get()
    self.assertEqual(col2_db.collection, ndb.Key('Collection','Key'))
    # test toplevel property
    col2.toplevel = key1
    key2 = col2.put()
    col2_db = key2.get()
    self.assertEqual(col2_db.toplevel, key1)




if __name__ == "__main__":
  unittest.main()
