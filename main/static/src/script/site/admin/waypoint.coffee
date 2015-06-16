window.init_waypoint_list = ->
  init_admin_waypoint_map()

window.init_waypoint_update = ->
  init_update_waypoint_map()


init_admin_waypoint_map = ->
  LOG "[init] admin waypoint map"
  map = init_map()
  markers = new L.MarkerClusterGroup({
    spiderLegPolylineOptions: {weight: 1.5, color: '#222'},
    maxClusterRadius: 40})
  #markers.addLayer(new L.Marker(getRandomLatLng(map)))
  #map.addLayer(markers)
  marker_group = []
  for waypoint in $('.waypoint-info')
    coord = $('.geo-point',waypoint).text().split(',')
    popup = $(waypoint).html()+"<br><a href=\"#{$('.point-edit-url',waypoint).text()}\" class=\"text-right\"> edit </a>"
    #marker_group.push(L.marker(coord).addTo(map).bindPopup(popup))
    markers.addLayer(L.marker(coord).bindPopup(popup))
  LOG marker_group
  #marker_feature = new L.featureGroup(marker_group)
  map.addLayer(markers)
  #marker_feature = new L.featureGroup(markers)
  map.fitBounds(markers.getBounds())


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
    # user once for only one marker
    map.on "click", (e) ->
      latlng = e.latlng.lat+","+e.latlng.lng
      $('#geo').val(latlng)
      _add_marker(e.latlng)
      loc_info latlng, (res) ->
        $('#name').val(res.name)
        $('#url').val(res.url)
        $('#description').val(res.description)
        if res.tags?
          $('#tags').val(res.tags.join())
        else
          $('#tags').val("")




