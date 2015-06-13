# coding: utf-8

import copy

from flask.ext import login
from flask.ext import wtf
from google.appengine.ext import ndb
import flask
import wtforms

import auth
import cache
import config
import model
import task
import util

from main import app


###############################################################################
# User List
###############################################################################
@app.route('/admin/collection/user')
@auth.admin_required
def collection_user_list():
  col_id = util.param('col_id')
  col_key = util.param('collection',ndb.Key)
  if col_id and not col_key:
    col_key = model.Collection.id_to_key(col_id)
  if col_key:
    col_db = col_key.get()
  else:
    col_db=None

  col_usr_dbs, col_usr_cursor = model.CollectionUser.get_dbs(collection=col_key)
  #permissions = list(UserUpdateForm._permission_choices)
  #permissions += util.param('permissions', list) or []
  return flask.render_template(
      'collection/collection_user_list.html',
      html_class='collection-user-list',
      title='Collection User List',
      col_usr_dbs=col_usr_dbs,
      col_db=col_db,
      next_url=util.generate_next_url(col_usr_cursor),
      api_url=None#flask.url_for('api.collection.list')
    )


###############################################################################
# Add User
###############################################################################
class CollectionUserAddForm(wtf.Form):
  email = wtforms.StringField(
      model.CollectionUser.user_email._verbose_name,
      [wtforms.validators.required(), wtforms.validators.length(min=3)]
    )

  permission = wtforms.SelectField(u'Permission',[wtforms.validators.required()],\
      choices=[\
      ("none","none"),\
      ("read", "read"),\
      ("write","write"),\
      ("admin","admin"),\
      ("creator","creator (don't user)")],default="read")

  def __init__(self, *args, **kwds):
    super(CollectionUserAddForm, self).__init__(*args, **kwds)


@app.route('/admin/collection/user/<col_key>/add/', methods=['GET', 'POST'])
@auth.admin_required
def collection_user_add(col_key=None):
  if col_key:
    col_key = ndb.Key(urlsafe=col_key)
    col_db = col_key.get()
  else:
    flask.abort(404)

  form = CollectionUserAddForm()
  if form.validate_on_submit():
    # get user key
    user_keys = model.User.query(model.User.email==form.email.data).fetch(5,keys_only=True)
    if not user_keys:
      flask.flash("Unknown user.",'danger')
      return flask.redirect(flask.url_for(
        'collection_user_list', order='-modified', collection=col_key.urlsafe()
        ))

    if form.permission.data == 'none':
      active = False
    else:
      active = True

    model.Collection.add_users(col_key,user_keys,permission=form.permission.data,active=active)
    return flask.redirect(flask.url_for(
        'collection_user_list', order='-modified', collection=col_key.urlsafe()
        ))

  return flask.render_template(
      'collection/collection_user_add.html',
      title=col_db.name or 'Add New User to Collection',
      html_class='collection-user-add',
      form=form,
      col_key=col_key,
      col_db=col_db,
      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
    )

@app.route('/admin/collection/user/<col_key>/remove/<user_key>', methods=['GET', 'POST'])
@auth.admin_required
def collection_remove_add(col_key=None,user_key=None):
  if col_key and user_key:
    col_key = ndb.Key(urlsafe=col_key)
    user_key = ndb.Key(urlsafe=user_key)
    col_db = col_key.get()
  else:
    flask.abort(404)

  model.Collection.remove_users(col_key,[user_key])
  return flask.redirect(flask.url_for(
      'collection_user_list', order='-modified', collection=col_key.urlsafe()
      ))

  return flask.render_template(
      'collection/collection_user_add.html',
      title=col_db.name or 'Add New User to Collection',
      html_class='collection-user-add',
      form=form,
      col_key=col_key,
      col_db=col_db,
      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
    )

