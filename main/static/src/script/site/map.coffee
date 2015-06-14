window.init_map = (center=[47,8],zoom=7)->
  init_leaflet_map(center,zoom)


init_leaflet_map = (center=[47,8],zoom=7) ->
  LOG "[init] map (c) leaflet"
# Define tile servers:
  thunderforestOutdoors = L.tileLayer(
    'http://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png',
    { attribution: '&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' })

  thunderforestOpenCycleMap = L.tileLayer(
     'http://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png',
     { attribution: '&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' })

  thunderforestTransport = L.tileLayer(
    'http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png',
    { attribution: '&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' })

  refugesHiking = L.tileLayer(
    'http://maps.refuges.info/hiking/{z}/{x}/{y}.png',
    { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors' })

  stamenWatercolor = L.tileLayer(
    'http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.{ext}', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: 'abcd',
    minZoom: 1,
    maxZoom: 16,
    ext: 'png' })

  osmMap = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png',
    { attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors' })

# time stamp needs to be updated from time to time
  geo_admin_timestamp = '20151231'
  geo_admin_url = 'http://wmts{s}.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/'+geo_admin_timestamp+'/3857/{z}/{x}/{y}.jpeg'

  swissGeoAdminMap = L.tileLayer(
    geo_admin_url, {
    attribution: '&copy; <a href="http://www.swisstopo.admin.ch/internet/swisstopo/en/home.html">swisstopo</a>',
    subdomains: ['10','11','12','13','14'],
    minZoom: 8 })

  map = L.map('map' , {
    layers: [thunderforestOutdoors],
    zoomControl : true }).setView(center, zoom)
# add an OpenStreetMap tile layer

  baseLayers = {
      "Swiss Topo": swissGeoAdminMap,
      "OSM Mapnik": osmMap,
      "Outdoor": thunderforestOutdoors,
      "Cycle": thunderforestOpenCycleMap,
      "Hiking" : refugesHiking,
      "Transport": thunderforestTransport
      "Watercolor": stamenWatercolor
          }

  L.control.layers(baseLayers).addTo(map)


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
   options.values = [['natural=peak', 'name', 'n']
                ['public_transport','name', 'nw']
                ['railway~"bus_stop|tram_stop|station|halt"', 'name' , 'nw']
                ['highway~"bus_stop|platform"', 'name' , 'nw']
                ['aerialway=station', 'name' , 'n']
                ['aerialway~"gondola|chair_lift|cable_car"', 'name' , 'nw']
                ['tourism', 'name', 'nw']
                ['bus=yes', 'name','n']
                ['train=yes', 'name','n']
                ['amenity=restaurant', 'name', 'nw']
                ['amenity=bicycle_parking', 'nw']
                ['amenity=bicycle_rental', 'nw']
                ['amenity=car_rental', 'nw']
                ['amenity=ferry_terminal', 'nw']
                ['amenity=fuel', 'nw']
                ['amenity=parking', 'nw']
                ['amenity=clinic', 'nw']
                ['amenity=hospital', 'nw']
                ['amenity=pharmacy', 'nw']
                ['amenity=cinema', 'nw']
                ['amenity=theatre', 'nw']
                ['amenity=grave_yard', 'nw']
                ['amenity=police', 'nw']
                ['amenity=shelter', 'nw']
                ['amenity=toilets', 'nw']
                ['amenity=water_point', 'nw']
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
      # build queries
      tests = ""
      LOG val[0...-1]
      LOG val[-1..]
      for t in val[0...-1]
        tests += "[#{t}]"
      if 'n' in val[-1..][0]
        qry += "node#{tests}(around:#{r},#{latlng});"
      if 'w' in val[-1..][0]
        qry += "way#{tests}(around:#{r},#{latlng});"
      if 'r' in val[-1..][0]
        qry += "rel#{tests}(around:#{r},#{latlng});"
      LOG qry
    qry += ');out tags qt 15;'
    LOG qry
    qry = encodeURIComponent(qry)

    $.getJSON overpass_api, "data="+qry, (data) ->
      LOG "Results from the overpass api call:"
      LOG data
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
            if value in ['hotel','alpine hut','hostel',
              'motel','camp_site','caravan_site']
              tags.push 'accomodation'
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

