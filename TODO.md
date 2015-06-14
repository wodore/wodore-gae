TODO
=====

General
---------
* Work with projections
* When possible work asyncron
* Check get_dbs if it is still collection=None
* check util.param(collection, ndb.Key ?? )
* Is it possible to use get_dbs from mixins?
* Write get_dbs tests

Init
------
* ~~Write an init function~~
  - ~~Change name to wodore~~
  - ~~Add Public/Global collection~~
  - Add Tags with relation (One class per tag with relation, color, category)

Collection
----------
* Save always collection id
* Give also an ID to the global collection?
* Create a collection mixin with appropriate functions
* Easier acces to name

Waypoint
---------
* Add remove waypoints (from list)

Icon
----
* Icon should be added to toplevel collection of not existing (?)
  - It should work like this, check again.j

Model
------
* Add tag type (or category) like waypoint, route, level. Multiple entries are possible.
* Schould icon data be saved together with esch tag?
* Re-do private, public and approved entries (same everywhere, well defined)
* Write tests for new Icon and Tag functions
* Add a copyright field for `Icon`
* Work with icon id, not urlsafe key

User
----
* Every new user needs a private collection
* Check if a key Key('User',e-mail) already exist
  - Replace the keys with the correct key

Control
--------
* Icon update
* Re-do list views (especially the filters)
* Add a back parameter which can be used for the back link
* Add browser caching for icons

Populate
---------
* ~~Add random icons to tags (and categories, or three different lists?)~~

GAE-init
--------
* ~~Update the newest version~~

For Later
---------
* Add a notification/status/what ever info class
