# difference-polygons

Given a "land" shapefile, remove all the shapes from one or more other shapefiles, producing a new shapefile that only has the "difference".

## Usage

    difference-polygons -l ./land_polygons.shp -r ./dont_want.shp -r water_polygon.shp -o not_covered.shp

### Min area filter

Use the `-a`/`--min-area` option to drop any resultant shapes that are less than this size (e.g. `-a 1e-09`). Area is based on units of the shapefiles's coordinate reference system.

## Licence

Copyright 2016, Rory McCann <rory@technomancy.org> GNU Affero General Public Licence, version 3 (or at your option, a later version). If you'd like a different non-AGPL licence, please contact me.
