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
# Tag List
###############################################################################
@app.route('/admin/tag')
@auth.admin_required
def tag_list():
  col_key = util.param('collection',ndb.Key)
  if col_key:
    col_db = col_key.get()
  else:
    col_db=None
  tag_dbs, tag_cursor = model.Tag.get_dbs(collection=col_key)
  return flask.render_template(
      'tag/tag_list.html',
      html_class='tag-list',
      title='Tag List',
      tag_dbs=tag_dbs,
      col_db=col_db,
      next_url=util.generate_next_url(tag_cursor),
      api_url=None#flask.url_for('api.Tag.list')
    )


###############################################################################
# Tag Update Form
###############################################################################
class TagUpdateForm(wtf.Form):
  name = wtforms.StringField(
      "Tag Name",
      [wtforms.validators.required()]
    )

  color = wtforms.StringField(
      "Color",
      [wtforms.validators.required()],
      default="blue"
    )

  icon  = wtforms.FileField(u'Icon')

  icon_key = wtforms.StringField(
      "Icon Key",
      [wtforms.validators.optional()])

  force_icon = wtforms.BooleanField("Force new icon",default=False)
  incr_counter = wtforms.BooleanField("Increase counter",default=False)

  def __init__(self, *args, **kwds):
    super(TagUpdateForm, self).__init__(*args, **kwds)


@app.route('/admin/tag/<collection>/update/<tag>', methods=['GET', 'POST'])
@app.route('/admin/tag/<collection>/update/', methods=['GET', 'POST'])
@app.route('/admin/tag/update/<tag>', methods=['GET', 'POST'])
@app.route('/admin/tag/update/', methods=['GET', 'POST'])
@auth.admin_required
def tag_update(collection=None, tag=None):
  collection = collection or util.param('collection')
  tag = tag or util.param('tag')
  if collection and collection!='global':
    col_db = ndb.Key(urlsafe=collection).get()
  else:
    collection = 'global'
    col_db = None
  if tag:
    tag_db = model.Tag.tag_to_key(tag,collection).get()
  else:
    tag_db = None


  form = TagUpdateForm(obj=tag_db)

  if form.validate_on_submit():
    if form.icon.data:
      fs = flask.request.files.getlist("icon")
      if fs:
        icon_struct = model.IconStructure(data=fs[0].read())
      else:
        icon_struct=None
    else:
      print "No Struct: no icon data"
      icon_struct=None
    if form.icon_key.data:
      icon_key = ndb.Key(urlsafe=form.icon_key.data)
    else:
      icon_key = None

    model.Tag.add(form.name.data,collection=collection,icon_key=icon_key,
      icon_structure=icon_struct,color=form.color.data,
      force_new_icon=form.force_icon.data,
      auto_incr=form.incr_counter.data)

    # get user key
    return flask.redirect(flask.url_for(
        'tag_list', order='-modified'
        ))

  return flask.render_template(
      'tag/tag_update.html',
      title= "Update Tag" if tag_db else "Add New Tag" ,#col_db or 'Add New Tag',
      html_class='tag-update',
      form=form,
      collection=collection,
      col_db=col_db,
      tag_db=tag_db,
      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
    )

