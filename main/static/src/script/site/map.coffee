window.init_map = (center=[47,8],zoom=7)->
  init_leaflet_map(center,zoom)


init_leaflet_map = (center=[47,8],zoom=7) ->
  LOG "[init] map (c) leaflet"
# create a map in the "map" div, set the view to a given place and zoom
  map = L.map('map').setView(center, zoom);
# add an OpenStreetMap tile layer
  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(map);

  return map

  """ Function which returns a overpass query
  options = { values : [ ['"natural"="peak"', 'n']
                ['"public_transport"', 'nw']
                ['"tourism"', 'nw']
                ... ],
              radius : 40}

  This returns a function which can be used to query overpass calls.
  The function needs the coordinates and as optional second argumend a radius.
  """
window.overpass_query = (options) ->
  clean_tags = (ar) ->
          if ar.length == 0
            return []
          res = {}
          res[ar[key]] = ar[key] for key in [0..ar.length-1]
          value.split('_').join(' ') for key, value of res
          clean_tags = (ar) ->
          if ar.length == 0
            return []
          res = {}
          res[ar[key]] = ar[key] for key in [0..ar.length-1]
          value.split('_').join(' ') for key, value of res

  if not options?
    options = {}

  if not options?.radius?
      options.radius = 40

  if not options?.values?
   options.values = [['"natural"="peak"', 'n']
                ['"public_transport"', 'nw']
                ['"tourism"', 'nw']
                ['"highway"="bus_stop"', 'n']
                ['"bus"="yes"','n']
                ['"train"="yes"','n']
                ['"amenity"="restaurant"', 'nw']
                ['"amenity"="bicycle_parking"', 'nw']
                ['"amenity"="bicycle_rental"', 'nw']
                ['"amenity"="car_rental"', 'nw']
                ['"amenity"="ferry_terminal"', 'nw']
                ['"amenity"="fuel"', 'nw']
                ['"amenity"="parking"', 'nw']
                ['"amenity"="clinic"', 'nw']
                ['"amenity"="hospital"', 'nw']
                ['"amenity"="pharmacy"', 'nw']
                ['"amenity"="cinema"', 'nw']
                ['"amenity"="theatre"', 'nw']
                ['"amenity"="grave_yard"', 'nw']
                ['"amenity"="police"', 'nw']
                ['"amenity"="shelter"', 'nw']
                ['"amenity"="toilets"', 'nw']
                ['"amenity"="water_point"', 'nw']
                ]



  (latlng, callback) ->
    if latlng?
      LOG "[ERROR] No coordinates are given ('latlng')"
    out = {}
    # overpass api
    overpass_api = "http://overpass-api.de/api/interpreter"
    overpass_api = "http://overpass.osm.rambler.ru/cgi/interpreter"
    overpass_api = "http://overpass.osm.ch/api/interpreter"

    r = options.radius

    qry = '[out:json];('
    for val in options.values
      if 'n' in val[1]
        qry += 'node['+val[0]+'](around:'+r+','+latlng+');'
      if 'w' in val[1]
        qry += 'way['+val[0]+'](around:'+r+','+latlng+');'
      if 'r' in val[1]
        qry += 'relation['+val[0]+'](around:'+r+','+latlng+');'
    qry += ');out body;'
    qry = encodeURIComponent(qry)

    $.getJSON overpass_api, "data="+qry, (data) ->
      #LOG data
      if data.elements[0]?
        if data.elements[0].tags.uic_name
          name = data.elements[0].tags.uic_name
        else
          name = data.elements[0].tags.name
        out.name = name
        out.url = data.elements[0].tags.url

        # check tags
        tags = []
        for key, value of data.elements[0].tags
          if key == 'tourism'
            tags.push key
            tags.push value
          if value == 'peak'
            tags.push value
          if (key == 'bus' and value == 'yes') or (key == 'highway' and value == 'bus_stop')
            tags.push 'bus'
            tags.push 'public_transport'
          if (key == 'train' and value == 'yes') or (key == 'highway' and value == 'train_stop')
            tags.push 'train'
            tags.push 'public_transport'
          if key == 'public_transport'
            tags.push key
          if key == 'amenity'
            tags.push value
        out.tags = clean_tags(tags)
      else
        out.name = ""
        out.url = ""
        out.tags = ""
      callback(out)
    return true

