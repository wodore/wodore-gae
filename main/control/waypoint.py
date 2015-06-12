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
  col_id = util.param('col_id')
  col_key = util.param('collection',ndb.Key)
  if col_id and not col_key:
    col_key = model.Collection.id_to_key(col_id)
  if col_key:
    col_db = col_key.get()
  else:
    col_db=None
  pt_dbs, waypoint_cursor = model.WayPoint.get_dbs(collection=col_key)
# get tags
  tag_dbs, tag_cursor = model.Tag.get_dbs(collection=col_key or \
    model.Collection.top_key(),order='-cnt')
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

  #collection = wtforms.StringField(
      #"Collection ID",
      #[wtforms.validators.required()],
    #)

  description = wtforms.StringField( "Description")
  url = wtforms.StringField( "URL")
  tags = wtforms.StringField( "tags", description="Tag names, separated by a comma",
      filters=[lambda x: ", ".join(x) if not isinstance(x, basestring) else x])
  geo = wtforms.StringField( "Geo", description="(longitude,latidude)")

  def __init__(self, *args, **kwds):
    super(WayPointUpdateForm, self).__init__(*args, **kwds)

# TODO user waypoint id, like user update!
@app.route('/admin/waypoint/<col_id>/update/<int:waypoint_id>/', methods=['GET', 'POST'])
@app.route('/admin/waypoint/<col_id>/update/', methods=['GET', 'POST'])
#@app.route('/admin/waypoint/update/', methods=['GET', 'POST'])
@auth.admin_required
def waypoint_update(col_id=None, waypoint_id=None):
  col_id = col_id or util.param('col_id')
  waypoint_id = waypoint_id or util.param('waypoint_id',int)

  if col_id and col_id!=model.Collection.top_id():
    col_db = model.Collection.id_to_key(col_id).get()
  else:
    flask.flash("Collection is needed.","danger")
    return flask.redirect(flask.url_for(
        'waypoint_list', order='-modified'
        ))
  if waypoint_id:
    pt_db = model.WayPoint.get_by_id(waypoint_id)
  else:
    pt_db = model.WayPoint(collection=col_db.key)

  form = WayPointUpdateForm(obj=pt_db)

  if form.validate_on_submit():
    print pt_db
    geo = ndb.GeoPt(form.geo.data)
    tags = map(unicode.strip, form.tags.data.split(','))
    pt_db.name = form.name.data
    pt_db.collection=col_db.key
    pt_db.description=form.description.data
    pt_db.url=form.url.data
    pt_db.geo=geo
    if tags:
      pt_db.update_tags(tags)
    pt_db.put()

    return flask.redirect(flask.url_for(
        'waypoint_list', order='-modified', col_id=col_id
        ))

  return flask.render_template(
      'waypoint/waypoint_update.html',
      title= "Update Waypoint" if pt_db else "Add New Waypoint" ,#col_db or 'Add New Tag',
      html_class='waypoint-update',
      form=form,
      collection=col_db.key,
      col_db=col_db,
      pt_db=pt_db,
      api_url=None#flask.url_for('api.user', col_key=col_db.key.urlsafe()) if col_db.key else ''
    )

