window.init_waypoint_list = ->
  init_admin_waypoint_map()


init_admin_waypoint_map = ->
  LOG "[init] admin waypoint map"
# create a map in the "map" div, set the view to a given place and zoom
  map = L.map('admin-waypoint-map').setView([47, 8], 7);
# add an OpenStreetMap tile layer
  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(map);


  for geo in $('.geo-point')
    coord = $(geo).text().split(',')
    L.marker(coord).addTo(map)


