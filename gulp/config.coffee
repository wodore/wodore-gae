paths = require './paths'

config =
  ext: [
    "#{paths.static.ext}/jquery/dist/jquery.js"
    "#{paths.static.ext}/moment/moment.js"
    "#{paths.static.ext}/nprogress/nprogress.js"
    "#{paths.static.ext}/bootstrap/js/alert.js"
    "#{paths.static.ext}/bootstrap/js/button.js"
    "#{paths.static.ext}/bootstrap/js/transition.js"
    "#{paths.static.ext}/bootstrap/js/collapse.js"
    "#{paths.static.ext}/bootstrap/js/dropdown.js"
    "#{paths.static.ext}/bootstrap/js/tooltip.js"
    "#{paths.static.ext}/leaflet-layer-overpass/dist/OverPassLayer.js"
    "#{paths.static.ext}/leaflet.markercluster/dist/leaflet.markercluster-src.js"
    #"#{paths.static.ext}/osmtogeojson/index.js"
    "#{paths.static.ext}/osmtogeojson/osmtogeojson.js"
    "#{paths.static.ext}/osmtogeojson/lodash.custom.js"
    #"#{paths.static.ext}/osmtogeojson/polygon_features.json"
    #"#{paths.static.ext}/leaflet-knn/leaflet-knn.js"
    #"#{paths.static.ext}/leaflet-knn/index.js"
    #"#{paths.static.ext}/sphere-knn/index.js"
    #"#{paths.static.ext}/sphere-knn/lib/binary.js"
    #"#{paths.static.ext}/sphere-knn/lib/kd.js"
    #"#{paths.static.ext}/sphere-knn/lib/spherekd.js"
  ]
  style: [
    "#{paths.src.style}/style.less"
  ]
  script: [
    "#{paths.src.script}/**/*.coffee"
  ]

module.exports = config
