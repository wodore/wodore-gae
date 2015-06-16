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
            radius : 80}

Returns a function which can be used to query overpass calls.
The function needs the coordinates as argument:
  get_info = overpass_query({radius:20})
  res = get_info("47.4,9.0")
  LOG res.tags
  LOG res.name
  ...
"""
window.overpass_query = (options) ->
  # INTERNAL FUNCTIONS
  # ------------------
  clean_tags = (ar) ->
          LOG "internal input #{ar}"
          LOG "internal value #{value}"
          LOG "internal res #{res}"
          if ar.length == 0
            return []
          res = {}
          res[ar[key]] = ar[key] for key in [0..ar.length-1]
          value.split('_').join(' ') for key, value of res

  # Calculates the distance between two points.
  # Only use this for close points (formula is not accurate)
  dist = (lon_from,lat_from,lon_to,lat_to) ->
         if not (lat_to? and lon_to?)
           return 10000
         phi_base = lat_from*0.01745329251
         theta_base = lon_from*0.01745329251
         phi = lat_to*0.01745329251
         theta = lon_to*0.01745329251
         dx = Math.cos(phi_base) * (theta - theta_base)
         dy = phi - phi_base
         return Math.sqrt(dx*dx+dy*dy)

  # ------------------
  # DEFINE OPTIONS
  if not options?
    options = {}

  if not options?.radius?
      options.radius = 80 # default (in meter)

  if not options?.values? #TODO amenity with ~ and |
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
    if not latlng?
      LOG "[ERROR] No coordinates are given ('latlng')"
    out = {}
    # overpass api server TODO: chose random, take another if one is down.
    overpass_api = "http://overpass-api.de/api/interpreter"
    overpass_api = "http://overpass.osm.rambler.ru/cgi/interpreter"
    overpass_api = "http://overpass.osm.ch/api/interpreter" # default

    r = options.radius
    qry = '[out:json];('

    # build queries
    for val in options.values
      tests = ""
      for t in val[0...-1]
        tests += "[#{t}]"
      if 'n' in val[-1..][0]
        qry += "node#{tests}(around:#{r},#{latlng});"
      if 'w' in val[-1..][0]
        qry += "way#{tests}(around:#{r},#{latlng});"
      if 'r' in val[-1..][0]
        qry += "rel#{tests}(around:#{r},#{latlng});"
    qry += ');out body qt 40;'
    qry = encodeURIComponent(qry)

    $.getJSON overpass_api, "data="+qry, (data) ->
      LOG "Results from the overpass api call:"
      LOG data.elements
      #LOG "GeoJSON" # it is possible to change the data to geo json
      #geoJson = osmtogeojson.toGeojson(data)


      # Sort the results form closest to furtherst
      latlngArray = latlng.split(',')
      lat = Number(latlngArray[0])
      lng = Number(latlngArray[1])
      elements = data.elements
      elements.sort (a,b) ->
        dist(lng,lat,Number(a.lon),Number(a.lat)) - \
        dist(lng,lat,Number(b.lon),Number(b.lat))
      LOG "Elements after sorting"
      LOG elements # debug

      if elements[0]?
        # find a name
        # 1. take the uic_name
        # 2. if not take name
        # 3. try the next element
        for n in elements
          if n.tags.uic_name
            name = n.tags.uic_name
            break
          else if n.tags.name
            name = n.tags.name
            break
          else
            name = ""
        out.name = name
        # check for a url
        if elements[0].tags.website?
          out.url = elements[0].tags.website
        else if elements[0].tags.wikipedia?
          wiki = elements[0].tags.wikipedia.split(':')
          out.url = "http://www.#{wiki[0]}.wikipedia.org/wiki/#{wiki[1]}"
        else if elements[0].tags.url?
          out.url = elements[0].tags.url
        else if elements[0].tags.facebook?
          out.url = elements[0].tags.facebook
        else
          out.url = ""

        if elements[0].tags.description?
          out.description = elements[0].tags.description
        else
          out.description = ""

        # check tags
        tags = []
        for key, value of elements[0].tags
          if key == 'tourism'
            tags.push key
            tags.push value
            if value in ['hotel','alpine hut','hostel',
              'motel','camp_site','caravan_site','wilderness hut']
              tags.push 'accomodation'
          if value == 'peak'
            tags.push value
          if (key == 'bus' and value == 'yes')\
          or (key == 'highway' and value == 'bus_stop')\
          or (key == 'railway' and value == 'bus_stop')
            tags.push 'bus'
            tags.push 'public_transport'
          if (key == 'train' and value == 'yes') \
          or (key == 'highway' and value == 'train_stop')\
          or (key == 'railway' and value == 'station')
            tags.push 'train'
            tags.push 'public_transport'
          if key == 'public_transport'
            tags.push key
          if key == 'amenity'
            tags.push value
        LOG tags
        out.tags = clean_tags(tags)
        LOG out.tags
      else
        out.name = ""
        out.url = ""
        out.description = ""
        out.tags = []
      callback(out)
    return true

