# coding: utf-8

from flask.ext import wtf
import flask
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Admin Stuff
###############################################################################
@app.route('/admin/populate')
@auth.admin_required
def admin_populate():
  return flask.render_template(
      'admin/populate/populate.html',
      title='Populate',
      html_class='populate',
    )


