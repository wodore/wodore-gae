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
  #permissions = list(UserUpdateForm._permission_choices)
  #permissions += util.param('permissions', list) or []
  return flask.render_template(
      'tag/tag_list.html',
      html_class='tag-list',
      title='Tag List',
      icon_dbs=icon_dbs,
      col_db=col_db,
      next_url=util.generate_next_url(icon_cursor),
      api_url=None#flask.url_for('api.Tag.list')
    )

  #
  ################################################################################
  ## Tag Update Form
  ################################################################################
  #class TagUpdateForm(wtf.Form):
  #  name = wtforms.StringField(
  #      "Tag Name",
  #      [wtforms.validators.required()]
  #    )
  #
  #  color = wtforms.StringField(
  #      "Color",
  #      [wtforms.validators.required()],
  #      default="blue"
  #    )
  #
  #  icon  = wtforms.FileField(u'Icon')
  #
  #  icon_key = wtforms.StringField(
  #      "Icon Key",
  #      [wtforms.validators.optional()])
  #
  #  def __init__(self, *args, **kwds):
  #    super(TagUpdateForm, self).__init__(*args, **kwds)
  #
  #
  #@app.route('/admin/tag/<col_key>/update/', methods=['GET', 'POST'])
  #@app.route('/admin/tag/update/', methods=['GET', 'POST'])
  #@auth.admin_required
  #def tag_update(col_key=None):
  #  if col_key and col_key!='global':
  #    col_db = ndb.Key(urlsafe=col_key).get()
  #  else:
  #    col_key = 'global'
  #    col_db = None
  #
  #  form = TagUpdateForm()
  #  if form.validate_on_submit():
  #    if form.icon.data:
  #      fs = flask.request.files.getlist("icon")
  #      print fs
  #      if fs:
  #        icon_struct = model.IconStructure(data=fs[0].read())
  #      else:
  #        print "No Struct: no file was uploaded"
  #        print form.icon.data
  #        print fs
  #        icon_struct=None
  #    else:
  #      print "No Struct: no icon data"
  #      icon_struct=None
  #    if form.icon_key.data:
  #      icon_key = ndb.Key(urlsafe=form.icon_key.data)
  #    else:
  #      icon_key = None
  #
  #    model.Tag.add(form.name.data,collection=col_key,icon_key=icon_key,
  #      icon_structure=icon_struct,color=form.color.data)
  #
  #    # get user key
  #    return flask.redirect(flask.url_for(
  #        'tag_list', order='-modified'
  #        ))
  #
  #  return flask.render_template(
  #      'tag/tag_update.html',
  #      title=col_db or 'Add New Tag',
  #      html_class='tag-update',
  #      form=form,
  #      col_key=col_key,
  #      col_db=col_db,
  #      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
  #    )
  #  # TODO
  #@app.route('/admin/collection/user/<col_key>/remove/<tag_key>', methods=['GET', 'POST'])
  #@auth.admin_required
  #def tag_remove(col_key=None,tag_key=None):
  #  if col_key and user_key:
  #    col_key = ndb.Key(urlsafe=col_key)
  #    user_key = ndb.Key(urlsafe=user_key)
  #    col_db = col_key.get()
  #  else:
  #    flask.abort(404)
  #
  #  model.Collection.remove_users(col_key,[user_key])
  #  return flask.redirect(flask.url_for(
  #      'collection_user_list', order='-modified', collection=col_key.urlsafe()
  #      ))
  #
  #  return flask.render_template(
  #      'collection/collection_user_add.html',
  #      title=col_db.name or 'Add New User to Collection',
  #      html_class='collection-user-add',
  #      form=form,
  #      col_key=col_key,
  #      col_db=col_db,
  #      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
  #    )
  #
