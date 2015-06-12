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
# Waypoint List
###############################################################################
@app.route('/admin/waypoint')
@auth.admin_required
def waypoint_list():
  col_key = util.param('collection',str)
  if col_key:
    col_db = ndb.Key(urlsafe=col_key).get()
  else:
    col_db=None
  pt_dbs, waypoint_cursor = model.WayPoint.get_dbs(collection=col_key)
# get tags
  tag_dbs, tag_cursor = model.Tag.get_dbs(collection=col_key or 'global',order='-cnt')
  return flask.render_template(
      'waypoint/waypoint_list.html',
      html_class='waypoint-list',
      title='Waypoint List',
      pt_dbs=pt_dbs,
      col_db=col_db,
      tag_dbs=tag_dbs,
      next_url=util.generate_next_url(waypoint_cursor),
      api_url=None#flask.url_for('api.Tag.list')
    )


###############################################################################
# Tag Update Form
###############################################################################
class WayPointUpdateForm(wtf.Form):
  name = wtforms.StringField(
      "Waypoint Name",
      [wtforms.validators.required()]
    )

  collection = wtforms.StringField(
      "Collection",
      [wtforms.validators.required()],
    )

  description = wtforms.StringField( "Description")
  url = wtforms.StringField( "URL")
  tags = wtforms.StringField( "tags", description="Tag names, separated by a comma",
      filters=[lambda x: ", ".join(x) if not isinstance(x, basestring) else x])
  geo = wtforms.StringField( "Geo", description="(longitude,latidude)")

  def __init__(self, *args, **kwds):
    super(WayPointUpdateForm, self).__init__(*args, **kwds)

# TODO user waypoint id, like user update!
@app.route('/admin/waypoint/<collection>/update/<int:waypoint_id>/', methods=['GET', 'POST'])
@app.route('/admin/waypoint/<collection>/update/', methods=['GET', 'POST'])
#@app.route('/admin/waypoint/update/', methods=['GET', 'POST'])
@auth.admin_required
def waypoint_update(collection=None, waypoint_id=None):
  collection = collection or util.param('collection')
  waypoint_id = waypoint_id or util.param('waypoint_id',int)

  if collection and collection!='global':
    col_db = ndb.Key(urlsafe=collection).get()
  else:
    flask.flash("Collection is needed.","danger")
    return flask.redirect(flask.url_for(
        'waypoint_list', order='-modified'
        ))
  if waypoint_id:
    pt_db = model.WayPoint.get_by_id(waypoint_id)
  else:
    pt_db = model.WayPoint(collection=collection)

  form = WayPointUpdateForm(obj=pt_db)

  if form.validate_on_submit():
    print pt_db
    geo = ndb.GeoPt(form.geo.data)
    tags = map(unicode.strip, form.tags.data.split(','))
    pt_db.name = form.name.data
    pt_db.collection=collection
    pt_db.description=form.description.data
    pt_db.url=form.url.data
    pt_db.geo=geo
    if tags:
      pt_db.update_tags(tags)
    pt_db.put()

    return flask.redirect(flask.url_for(
        'waypoint_list', order='-modified', collection=collection
        ))

  return flask.render_template(
      'waypoint/waypoint_update.html',
      title= "Update Waypoint" if pt_db else "Add New Waypoint" ,#col_db or 'Add New Tag',
      html_class='waypoint-update',
      form=form,
      collection=collection,
      col_db=col_db,
      pt_db=pt_db,
      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
    )

