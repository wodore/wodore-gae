window.init_map = ->
  init_leaflet_map()


init_leaflet_map = (latLng=[47,8],zoom=7) ->
  LOG "[init] map (c) leaflet"
# create a map in the "map" div, set the view to a given place and zoom
  map = L.map('map').setView(latLng, zoom);
# add an OpenStreetMap tile layer
  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(map);

  return map

