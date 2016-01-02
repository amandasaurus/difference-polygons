import sys, fiona
import shapely.ops
from shapely.geometry import shape, mapping
from rtree import index

def is_multi(geom):
    return geom.geom_type.startswith("Multi") or geom.geom_type == 'GeometryCollection'

def remove_zero_areas(geom):
    result = []
    if not is_multi(geom):
        if geom.area > 0:
            result.append(geom)
    else:
        for part in geom.geoms:
            if part.area > 0:
                result.append(part)

    return result

def do_difference(filename_a, filename_b, output_filename):
    print "Reading in {}".format(filename_a)
    with fiona.open(filename_a) as fpa:
        output_crs = fpa.crs

        data_a = [shape(x['geometry']) for x in fpa]

    geom_index = index.Index()
    print "Reading in {}".format(filename_b)
    with fiona.open(filename_b) as fpb:
        data_b = [shape(x['geometry']) for x in fpb]
        for pos, b_obj in enumerate(data_b):
            geom_index.insert(pos, b_obj.bounds)


    num_as = len(data_a)
    output_geoms = []
    for idx, a_geom in enumerate(data_a):
        sys.stdout.write("Looking at object {:,} of {:,}\r".format(idx, num_as))
        sys.stdout.flush()
        possible_bs = shapely.ops.cascaded_union([data_b[pos] for pos in geom_index.intersection(a_geom.bounds)])
        new_geom = a_geom.difference(possible_bs)
        output_geoms.append(new_geom)
    print "\n"

    print "Merging all geoms together..."
    output_geom = shapely.ops.cascaded_union(output_geoms)

    # split into companent shapes
    output_geoms = output_geom.geoms

    print "Writing output"
    with fiona.open(output_filename, 'w', 'ESRI Shapefile', crs=output_crs, schema={'geometry': 'Polygon', 'properties': {}}) as output_fp:
        for geom in output_geoms:
            output_fp.write({'properties': {}, 'geometry': mapping(geom)})

def main(argv):
    filename_a, filename_b, output_filename = argv
    do_difference(filename_a, filename_b, output_filename)

if __name__ == '__main__':
    main(sys.argv[1:])
