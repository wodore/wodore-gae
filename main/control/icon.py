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
# Return Icon
###############################################################################
@app.route('/icon/<icon_key>')
@auth.login_required
def show_icon(icon_key):
  #print icon_keyy
  response = flask.make_response(ndb.Key(urlsafe=icon_key).get().icon.data)
  response.content_type = 'image/svg+xml'
  return response

###############################################################################
# Icon List
###############################################################################
@app.route('/admin/icon')
@auth.admin_required
def icon_list():
  col_key = util.param('collection',str)
  if col_key:
    col_db = ndb.Key(urlsafe=col_key).get()
  else:
    col_db=None
  icon_dbs, icon_cursor = model.Icon.get_dbs(collection=col_key)
  print icon_dbs
  #permissions = list(UserUpdateForm._permission_choices)
  #permissions += util.param('permissions', list) or []
  return flask.render_template(
      'icon/icon_list.html',
      html_class='icon-list',
      title='Icon List',
      icon_dbs=icon_dbs,
      col_db=col_db,
      next_url=util.generate_next_url(icon_cursor),
      api_url=None#flask.url_for('api.Tag.list')
    )



###############################################################################
# Tag Update Form
###############################################################################
class IconUpdateForm(wtf.Form):
  name = wtforms.StringField(
      "Tag Name",
      [wtforms.validators.required()]
    )

  icon  = wtforms.FileField(u'Icon')

  incr_counter = wtforms.BooleanField("Increase counter",default=False)

  def __init__(self, *args, **kwds):
    super(IconUpdateForm, self).__init__(*args, **kwds)


@app.route('/admin/icon/<collection>/update/<icon_key>', methods=['GET', 'POST'])
@app.route('/admin/icon/<collection>/update/', methods=['GET', 'POST'])
@app.route('/admin/icon/update/<icon_key>', methods=['GET', 'POST'])
@app.route('/admin/icon/update/', methods=['GET', 'POST'])
@auth.admin_required
def icon_update(collection=None, icon_key=None):
  collection = collection or util.param('collection')
  icon_key = icon_key or util.param('icon_key')
  if collection and collection!='global':
    col_db = ndb.Key(urlsafe=collection).get()
  else:
    collection = 'global'
    col_db = None
  if icon_key:
    icon_db = icon_key.get()
  else:
    icon_db = None


  form = IconUpdateForm(obj=icon_db)
  if form.validate_on_submit():
    fs = flask.request.files.getlist("icon")
    if fs:
      icon_struct = model.IconStructure(data=fs[0].read())
    else:
      icon_struct=None
# TODO
    model.Icon.add(form.name.data,collection=collection,icon_key=icon_key,
      icon_structure=icon_struct,color=form.color.data,
      force_new_icon=form.force_icon.data,
      auto_incr=form.incr_counter.data)

    # get user key
    return flask.redirect(flask.url_for(
        'icon_list', order='-modified'
        ))

  return flask.render_template(
      'icon/icon_update.html',
      title= "Update Icon" if icon_db else "Add New Icon" ,#col_db or 'Add New Tag',
      html_class='icon-update',
      form=form,
      collection=collection,
      col_db=col_db,
      tag_db=tag_db,
      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
    )

