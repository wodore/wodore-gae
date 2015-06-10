$ ->
  init_common()

$ -> $('html.welcome').each ->
  LOG('init welcome')


$ -> $('html.auth').each ->
  init_auth()

$ -> $('html.feedback').each ->

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()

$ -> $('html.admin-config').each ->
  init_admin_config()

# custom wodore

$ -> $('html.waypoint-list').each ->
  init_waypoint_list()


$ -> $('html.waypoint-update').each ->
  init_waypoint_update()
