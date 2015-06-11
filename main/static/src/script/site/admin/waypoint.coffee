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
  # internal add marker function
  _add_marker = (latlng, name="") ->
    marker = L.marker(latlng, {
                      draggable:true
                  }).addTo(map)
    marker.on "dragend", (e) ->
      $('#geo').val(e.target._latlng.lat+","+e.target._latlng.lng)
    return marker

  LOG "[init] update waypoint map"

  loc_info = overpass_query()
  geo = $('#geo').val().split(',')
  if geo[0]
    map = init_map(geo,12)
  else
    LOG "Add new waypoint"
    map = init_map([46.9,9],10)


  if geo[0]
    _add_marker(geo)
  else
    map.once "click", (e) ->
#map.on "click", (e) ->
      latlng = e.latlng.lat+","+e.latlng.lng
      $('#geo').val(latlng)
      _add_marker(e.latlng)
      loc_info latlng, (res) ->
        $('#name').val(res.name)
        $('#url').val(res.url)
        $('#tags').val(res.tags.join())




