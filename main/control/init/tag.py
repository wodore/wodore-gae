class tag_init(object):
 tags_new = {
    "tags_special_scale" : {
          "tags" : ("hangover","advanced","ohh shit","just 2 beer","just 3 beer","just a beer"),
          "color" : "darkblue",
          "category" : ["level"], "incr" : 20
    },
    "tags_hiking_scale" : {
          "tags" : ("T1","T2","T3","T4","T5","T6","T4-","T5-","T6-","T4+","T5+","T6+"),
          "color" : "orange",
          "category" : ["level"], "incr" : 20
    },
  "tags_touren_scale" : {
          "tags" : ("L","L+","WS-","WS","WS-","ZS-","ZS","ZS+","S-","S","S+"),
          "color" : "darkorange",
          "category" : ["level"], "incr" : 20
    },
  "tags_accomodation" : {
          "tags" : ("hotel","alpine hut","accomodation","hostel", "tourism", "wilderness hut"),
          "color" : "lightblue",
          "category" : ["waypoint"], "incr" : 20
    },

  "tags_public_transport" : {
          "tags" : ("public transport","train","bus","cable car","cable lift","ferry"),
          "color" : "lightgreen",
          "category" : ["waypoint", "route"], "incr" : 20
    },
  "tags_nature" : {
          "tags" : ("peak","hill","glacier","forest","lake", "river"),
          "color" : "green",
          "category" : ["waypoint","route"], "incr" : 20
    },
  "tags_transport" : {
          "tags" : ("parking","fuel"),
          "color" : "blue",
          "category" : ["waypoint"], "incr" : 20
    },
  "tags_food_and_drink" : {
          "tags" : ("food","restaurant","bar","pub","picnic"),
          "color" : "brown",
          "category" : ["waypoint", "route"], "incr" : 20
    },
  "tags_misc" : {
          "tags" : ("information","bbq","drinking water"),
          "color" : "black",
          "category" : ["waypoint"], "incr" : 20
    },
  "tags_entertainment" : {
          "tags" : ("fun","cinema","theatre","entertainment"),
          "color" : "purple",
          "category" : ["waypoint", "route"], "incr" : 20
    },
  "tags_time" : {
          "tags" : ("winter","summer","fall","autumn","all day","half day","night","evening","morning","afternoon"),
          "color" : "pink",
          "category" : ["waypoint", "route"], "incr" : 20
    },
  "tags_categories" : {
   "tags" : ("ski tour","hiking","mountain bike","biking","alpine tour",
                "climbing","trail running","running","snow shoes","trekking"),
          "color" : "purple",
          "category" : ["route"], "incr" : 20
    }
  }
######### FOR RELATIONS
 tags_relation = {
    "tags_hiking_scale_relation1" : {
          "tags" : ("T1","T2","T3","hangover"),
          "incr" : 30
    },
    "tags_hiking_scale_relation2" : {
          "tags" : ("T3","T4","T4-","T5-","T4+","just 3 beer","just 2 beer"),
          "incr" : 30
    },
    "tags_hiking_scale_relation3" : {
          "tags" : ("T5","T6","T5-","T6-","T5+","T6+", "advanced","advanced hiking","ohh shit","just a beer"),
          "incr" : 30
    },
    "tags_hiking_scale_relation4" : {
          "tags" : ("hiking", "hangover", "T1","T2","T3","T4","T5","T6","T4-","T5-","T6-","T4+","T5+","T6+"),
          "incr" : 30
    },
    "tags_hiking_scale_relation5" : {
          "tags" : ("T5","T6","T5-","T6-","T5+","T6+", "advanced","ohh shit","just a beer"),
          "incr" : 30
    },
    "tags_time_relation1" : {
          "tags" : ("winter","skitour","snow shoes"),
          "incr" : 30
    },
    "tags_time_relation2" : {
          "tags" : ("fall","summer","autumn","hiking","mountainbike","climbing","trail"),
          "incr" : 30
    },
    "tags_time_relation3" : {
          "tags" : ("summer","autumn","alpinism"),
          "incr" : 30
    },
   "tags_accomodation_relation1" : {
          "tags" : ("alpin hut","wilderness hut","hut"),
          "incr" : 30
    },
   "tags_accomodation_relation2" : {
          "tags" : ("hotel","motel","hostel"),
          "incr" : 10
    },
   "tags_accomodation_relation3" : {
          "tags" : ("alpin hut","accomodation","hut"),
          "incr" : 40
    },
   "tags_accomodation_relation4" : {
          "tags" : ("wilderness hut","accomodation","hut"),
          "incr" : 40
    },
   "tags_accomodation_relation5" : {
          "tags" : ("hostel","accomodation"),
          "incr" : 40
    },
   "tags_accomodation_relation6" : {
          "tags" : ("hotel","accomodation"),
          "incr" : 40
    },

 }

