import sys, fiona
import shapely.ops
from shapely.geometry import shape, mapping

def is_multi(geom):
    return geom.geom_type.startswith("Multi") or geom.geom_type == 'GeometryCollection'



def do_difference(filename_a, filename_b, output_filename):
    print "Reading in {}".format(filename_a)
    with fiona.open(filename_a) as fpa:
        output_crs = fpa.crs

        data_a = [shape(x['geometry']) for x in fpa]

    print "Reading in {}".format(filename_b)
    with fiona.open(filename_b) as fpb:
        data_b = [shape(x['geometry']) for x in fpb]


    num_as = len(data_a)

    with fiona.open(output_filename, 'w', 'ESRI Shapefile', crs=output_crs, schema={'geometry': 'Polygon', 'properties': {}}) as output_fp:
        for idx, a_geom in enumerate(data_a):
            sys.stdout.write("Looking at object {} of {}\r".format(idx, num_as))
            sys.stdout.flush()
            possible_bs = shapely.ops.cascaded_union([x for x in data_b if x.intersects(a_geom)])
            new_geom = a_geom.difference(possible_bs)
            if is_multi(new_geom):
                for g in new_geom:
                    output_fp.write({'properties': {}, 'geometry': mapping(g)})
            else:
                output_fp.write({'properties': {}, 'geometry': mapping(new_geom)})

def main(argv):
    filename_a, filename_b, output_filename = argv
    do_difference(filename_a, filename_b, output_filename)

    if __name__ == '__main__':
    main(sys.argv[1:])
