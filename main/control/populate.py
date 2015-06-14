# coding: utf-8

from google.appengine.ext import ndb

from flask.ext import wtf
import flask
import wtforms

import auth
import config
import model
import util

from main import app

import random

# Generate useful random data
from faker import Factory

###############################################################################
# Help Functions
###############################################################################
def _return_state(state):
  """Returns either True or False depending on state.

  State can be "true", "false", or "random."""
  if state == "true":
    return True
  elif state == "false":
    return False
  else:
    return True if round(random.random()) else False
###############################################################################
# Population Page
###############################################################################
@app.route('/admin/populate', methods=['GET'])
@auth.admin_required
def admin_populate(form=None):
  form_user = PopulateUserForm()
  form_col = PopulateCollectionForm()
  form_col_user = PopulateCollectionUserForm()
  form_tag = PopulateTagForm()
  form_icon = PopulateIconForm()
  form_waypoint = PopulateWayPointForm()

  return flask.render_template(
      'admin/populate/populate.html',
      title='Populate',
      html_class='populate',
      form_user=form_user,
      form_col=form_col,
      form_col_user=form_col_user,
      form_tag=form_tag,
      form_icon=form_icon,
      form_waypoint=form_waypoint
    )

## USER ----------------------
@app.route('/admin/populate/user', methods=['POST'])
@auth.admin_required
def admin_populate_user():
  # Create a fake instance
  fake = Factory.create()
  form_user = PopulateUserForm()
  if form_user.validate_on_submit():
    user_dbs = []
    nr = form_user.number_of_users.data
    if nr > 1000:
      flask.flash('You cannot create more than 1000 new users at once. Try again!',\
          category='danger')
      return flask.redirect(flask.url_for('admin_populate'))
    for i in range(nr):
      user = fake.profile(fields=['name','username','mail'])
      user_dbs.append(model.User(name=user['name'],\
          username=user['username'],
          email=user['mail'],
          active=_return_state(form_user.active.data),
          admin=_return_state(form_user.admin.data),
          verified=_return_state(form_user.verified.data)))
    keys = ndb.put_multi(user_dbs)
    for key in keys:
      # run the new user function
      auth.new_user(key)
    flask.flash('Created {nr} new users'.\
          format(nr=len(user_dbs)), category='success')
  return flask.redirect(flask.url_for('admin_populate'))

###############################################################################
# Collection
@app.route('/admin/populate/collection', methods=['POST'])
@auth.admin_required
def admin_populate_collection():
  fake = Factory.create()
  form_col = PopulateCollectionForm()
# Somehow `validate_on_submit()` is False even when submited, why?
  if form_col.validate_on_submit() or True:
    print "Collection Valid"
    col_dbs = []
    nr = form_col.number_of_collections.data
    if nr > 200:
      flask.flash('You cannot create more than 200 new collections at once. Try again!',\
          category='danger')
      return flask.redirect(flask.url_for('admin_populate'))
    creator_random = False
    if form_col.creator.data == "current":
      creator = auth.current_user_key()
    elif form_col.creator.data == "search":
      user_dbs, _ = model.User.get_dbs(email=form_col.user_email.data,limit=2)
      if user_dbs:
        creator = user_dbs[0].key
      else:
        flask.flash('User with email {} not found. Try again!'.\
            format(form_col.user_email.data),\
            category='danger')
        return flask.redirect(flask.url_for('admin_populate'))

    else:
      creator_random = True
      user_keys = model.User.query().fetch(limit=5000, keys_only=True)
    for i in range(nr):
      if creator_random:
        creator = random.choice(user_keys)
        print creator
      sentence_length = int(form_col.desc_min.data+\
          random.random()*(form_col.desc_max.data-form_col.desc_min.data))
      if sentence_length <= 5:
        desc = ""
      else:
        desc = fake.text(max_nb_chars=sentence_length)

      model.Collection.create(name=fake.word(),
          creator=creator,
          description=desc,
          active=_return_state(form_col.active.data),
          public=_return_state(form_col.public.data))

    flask.flash('Created {nr} new collections'.\
          format(nr=nr), category='success')
  else:
    print "Collection NOT Valid"
  return flask.redirect(flask.url_for('admin_populate'))


###############################################################################
# CollectionUser
@app.route('/admin/populate/collection_user', methods=['POST'])
@auth.admin_required
def admin_populate_collection_user():
  #TODO add this to a task!
  # it takes quite a long time
  #fake = Factory.create()
  form_col_user = PopulateCollectionUserForm()
  permission_list = ('none','read','write','admin','creator')
# Somehow `validate_on_submit()` is False even when submited, why?
  if form_col_user.validate_on_submit() or True:
    user_keys = model.User.query().fetch(limit=5000, keys_only=True)
    cnt = 0
    cnt_users = 0
    for key in model.Collection.qry(private=False,public=False)\
        .fetch(keys_only=True, limit=form_col_user.max_collections.data):
      user_nr = int(form_col_user.user_min.data+\
          random.random()*(form_col_user.user_max.data-form_col_user.user_min.data))
      cnt_users += user_nr
      users = random.sample(user_keys,user_nr)
      if form_col_user.permission.data == "random":
        users_perm = []
        for user in users:
          users_perm.append((user,random.choice(permission_list)))
        model.Collection.add_users(key,users_perm,permission=False)
      else:
        model.Collection.add_users(key,users,\
            permission=form_col_user.permission.data)
      cnt += 1
    flask.flash('Added a total of {usr_nr} users to {nr} collections'.\
          format(usr_nr=cnt_users, nr=cnt), category='success')

  return flask.redirect(flask.url_for('admin_populate'))
#



###############################################################################
# Tag
@app.route('/admin/populate/tag/', methods=['POST'])
@auth.admin_required
def admin_populate_tag():
  form_tag = PopulateTagForm()
  if form_tag.validate_on_submit() or True:
    if form_tag.random_tags.data:
      if form_tag.max_tags.data > 500:
        flask.flash('Not more than 500 random tags can be created at once. Try again!',\
            category='danger')
        return flask.redirect(flask.url_for('admin_populate'))

      fake = Factory.create()
      tags = fake.words(nb=form_tag.max_tags.data)
    else:
      tags = form_tag.tags.data.split(', ')
    # Are icon needed as well?
    if form_tag.icon.data:
      icon_keys, _ = model.Icon.get_dbs(keys_only=True,limit=2000, collection=model.Collection.top_key())
    else:
      icon_keys = None
    cnt = 0
    incr = True if form_tag.incr.data=='true' else False
    for tag in tags:
      icon_key = random.choice(icon_keys) if icon_keys else None
      model.Tag.add(tag,auto_incr=incr,icon_key=icon_key)
      cnt += 1
    flask.flash('Added {nr} tags'.\
          format(nr=cnt), category='success')

  return flask.redirect(flask.url_for('admin_populate'))
#

###############################################################################
# Icon
@app.route('/admin/populate/icon', methods=['POST'])
@auth.admin_required
def admin_populate_icon():
  form_icon = PopulateIconForm()
  if form_icon.validate_on_submit() or True:
    names = ""
    fs = flask.request.files.getlist("icon")
    cnt = 0
    for f in fs:
      icon = f.read()
      model.Icon.create(icon=icon,
          name=f.filename.split('.')[0])
      names += f.filename.split('.')[0]+" "
      cnt += 1

    flask.flash('Added {} icon: {}'.format(cnt, names), category='success')

  return flask.redirect(flask.url_for('admin_populate'))

###############################################################################
# WayPoint
@app.route('/admin/populate/waypoint', methods=['POST'])
@auth.admin_required
def admin_populate_waypoint():
  form_waypoint = PopulateWayPointForm()
  if form_waypoint.validate_on_submit() or True:
    # Create a fake instance
    fake = Factory.create()
    # create collection list
    if form_waypoint.collection.data == "random":
      if form_waypoint.collection_user.data:
        email = form_waypoint.collection_user.data
        col_usr_dbs = model.CollectionUser.qry(user_email=email).\
            fetch(limit=form_waypoint.max_collections.data)
        if not col_usr_dbs:
          flask.flash("No colleciton found for user {}."\
              .format(email), category='danger')
          return flask.redirect(flask.url_for('admin_populate'))
        col_keys=[]
        for db in col_usr_dbs:
          col_keys.append(db.collection)
      else:
        col_keys = model.Collection.qry().\
            fetch(limit=form_waypoint.max_collections.data,\
            keys_only=True)

    elif form_waypoint.collection.data == "search":
      col_keys = [ndb.Key(urlsafe=form_waypoint.collection_key.data)]
    else: # not is not implemented/possible
      flask.flash("Key error, 'none' is not possible.", category='danger')
      return flask.redirect(flask.url_for('admin_populate'))
# set up tag list
    if form_waypoint.tags.data == "list":
      tag_list = form_waypoint.tag_list.data.split(', ')
    elif form_waypoint.tags.data == "random":
      tag_dbs = model.Tag.qry(collection=model.Collection.top_key()).fetch(limit=10000)
      tag_list = []
      for db in tag_dbs:
        tag_list.append(db.name)
    else:
      tag_list = None

    dbs = []
    cnt = 0
# create waypoints
    for key in col_keys:
      for i in range(0,form_waypoint.max_waypoints.data):
        name = fake.word()
        desc = fake.sentence()
# roughly switzerland
        lat = random.random()*3+45
        lng = random.random()*4 + 6
        geo = ndb.GeoPt(lat,lng)
        db = model.WayPoint(name=name,description=desc,collection=key,geo=geo)
        if tag_list:
          tag_nr = int(random.random()*form_waypoint.max_tags.data)
          while tag_nr > len(tag_list):
            tag_nr -=1
          db.add_tags(random.sample(tag_list,tag_nr))
        dbs.append(db)
        cnt += 1

    ndb.put_multi(dbs)
    flask.flash('Added {} waypoints'.format(cnt), category='success')

  return flask.redirect(flask.url_for('admin_populate'))

#
#
###############################################################################
# Population Forms
###############################################################################
# User
class PopulateUserForm(wtf.Form):
  number_of_users = wtforms.IntegerField(
      u'New Users (#)',
      [wtforms.validators.required()],
      default=100
    )

  verified = wtforms.RadioField(u'Verified',[wtforms.validators.required()],\
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down"),("random","random")],default="true")
  admin = wtforms.RadioField(u'Admin',[wtforms.validators.required()], \
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down"),("random","random")],default="random")
  active = wtforms.RadioField(u'Active',[wtforms.validators.required()],\
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down"),("random","random")],default="true")

  def __init__(self, *args, **kwds):
    super(PopulateUserForm, self).__init__(*args, **kwds)


###############################################################################
# Collection
class PopulateCollectionForm(wtf.Form):
  number_of_collections = wtforms.IntegerField(
      u'New Collections (#)',
      [wtforms.validators.required()],
      default=10
    )
  desc_min = wtforms.IntegerField(
      u'Min Description Length',
      [wtforms.validators.required()],
      default=5
    )
  desc_max = wtforms.IntegerField(
      u'Max Description Length',
      [wtforms.validators.required()],
      default=65
    )

  user_email = wtforms.StringField(
      u'Creator email',description="Only if search is active",
      validators=[wtforms.validators.Email()],
    )

  creator = wtforms.RadioField(u'Creator',[wtforms.validators.required()],\
      choices=[("current", "Current user"),\
      ("random","Random users"),("search","Search for a user")],default="current")

  public = wtforms.RadioField(u'Public',[wtforms.validators.required()], \
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down"),("random","random")],default="false")

  active = wtforms.RadioField(u'Active',[wtforms.validators.required()],\
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down"),("random","random")],default="true")

  def __init__(self, *args, **kwds):
    super(PopulateCollectionForm, self).__init__(*args, **kwds)

###############################################################################
# CollecitonUser
class PopulateCollectionUserForm(wtf.Form):
  user_min = wtforms.IntegerField(
      u'Min user to collection',
      [wtforms.validators.required()],
      default=5
    )
  user_max = wtforms.IntegerField(
      u'Max user to collection',
      [wtforms.validators.required()],
      default=20
    )

  max_collections = wtforms.IntegerField(
      u'Max collections',
      [wtforms.validators.required()],
      default=30
    )

  permission = wtforms.RadioField(u'Permission',[wtforms.validators.required()],\
      choices=[\
      ("none","ban"),\
      ("read", "book"),\
      ("write","pencil"),\
      ("admin","user"),\
      ("creator","user-plus"),\
      ("random","random")],default="read")

  def __init__(self, *args, **kwds):
    super(PopulateCollectionUserForm, self).__init__(*args, **kwds)

###############################################################################
# Tag
class PopulateTagForm(wtf.Form):
  DEFAULT_TAGS="""hiking, skitour, ski, mountain, peak, hill, T1, T2, T3, T4, T5, T6, -, +, river, lake, forest, over 3000, over 4000, bike, moutainbike, running, hangover, accomodation, hut, hostel, hotel, bus station, train station, public transport, station, restaurant, food, supermarket, beer, break, view, danger, ship, train, cable car, parking"""
  tags = wtforms.TextAreaField(
      u'Tag list',
      default=DEFAULT_TAGS,
      description="Separate the tags with a comma"
    )
  max_tags = wtforms.IntegerField(
      u'Max random tags',
      default=50
    )

  random_tags = wtforms.BooleanField(u'Random tags',default=False)

  incr = wtforms.RadioField(u'Increment',[wtforms.validators.required()], \
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down")],default="false")

  icon = wtforms.RadioField(u'Add Icon',[wtforms.validators.required()], \
      choices=[("true", "thumbs-o-up"),\
      ("false","thumbs-o-down")],default="false",\
      description="Only gobal icon which already exist.")


  def __init__(self, *args, **kwds):
    super(PopulateTagForm, self).__init__(*args, **kwds)

###############################################################################
# Icon
class PopulateIconForm(wtf.Form):
  icon  = wtforms.FileField(u'Icons')

  def __init__(self, *args, **kwds):
    super(PopulateIconForm, self).__init__(*args, **kwds)

###############################################################################
# WayPoint
class PopulateWayPointForm(wtf.Form):
  collection = wtforms.RadioField(u'Collection',[wtforms.validators.required()],\
      description='How should collection be used (random, none (toplevel), search).',
      choices=[\
      ("random", "random"),\
      ("search","key")],default="random")

  max_waypoints = wtforms.IntegerField(
      u'Max waypoints per collection',
      [wtforms.validators.required()],
      description='How many waypoints are added to one collection',
      default=5
    )

  max_collections = wtforms.IntegerField(
      u'Max collections',
      [wtforms.validators.required()],
      description='How many collections are used to add waypoints, only if random',
      default=10
    )
  collection_user = wtforms.StringField(
      u'Collection user email.',
      description='Only take random collection with this user.'
    )

  collection_key = wtforms.StringField(
      u'URL safe collection key.',
      [wtforms.validators.required()],
      description='Only if search.'
    )

  tags = wtforms.RadioField(u'Random or from list',[wtforms.validators.required()],\
      description='Add random tags from a list or from all possible tags, or don\'t add tags at all.',
      choices=[\
      ("list","list"),\
      ("random", "random"),\
      ("none", "ban")\
      ],default="list")

  max_tags = wtforms.IntegerField(
      u'Max tags per collection',
      [wtforms.validators.required()],
      description='Can also be less (random).',
      default=10
    )

  DEFAULT_TAGS="""hiking, skitour, ski, mountain, peak, hill, T1, T2, T3, T4, T5, T6, -, +, river, lake, forest, over 3000, over 4000, bike, moutainbike, running, hangover, accomodation, hut, hostel, hotel, bus station, train station, public transport, station, restaurant, food, supermarket, beer, break, view, danger, ship, train, cable car, parking"""
  tag_list = wtforms.TextAreaField(
      u'Tag list',
      default=DEFAULT_TAGS,
      description="Separate the tags with a comma"
    )

  def __init__(self, *args, **kwds):
    super(PopulateWayPointForm, self).__init__(*args, **kwds)

