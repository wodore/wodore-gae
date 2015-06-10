window.init_waypoint_list = ->
  init_admin_waypoint_map()

window.init_waypoint_update = ->
  init_update_waypoint_map()


init_admin_waypoint_map = ->
  LOG "[init] admin waypoint map"
  map = init_map()
  for geo in $('.geo-point')
    coord = $(geo).text().split(',')
    L.marker(coord).addTo(map)


init_update_waypoint_map = ->
  LOG "[init] update waypoint map"
  map = init_map()
  coord = $('#geo').val().split(',')

  add_marker = (latlng, name="") ->
    marker = L.marker(latlng, {
                      draggable:true
                  }).addTo(map)
    marker.on "dragend", (e) ->
      LOG e
      $('#geo').val(e.target._latlng.lat+","+e.target._latlng.lng)
    return marker

  if coord[0]
    add_marker(coord)
  else
    map.once "click", (e) ->
      $('#geo').val(e.latlng.lat+","+e.latlng.lng)
      add_marker(e.latlng)



