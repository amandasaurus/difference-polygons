import sys, fiona
import shapely.ops
from shapely.geometry import shape, mapping
from rtree import index
import argparse

def is_multi(geom):
    return geom.geom_type.startswith("Multi") or geom.geom_type == 'GeometryCollection'


# todo add split all multis into singles func
def split_out_all_multis(geoms):
    results = []
    for geom in geoms:
        if geom.geom_type == 'Polygon':
            results.append(geom)
        elif geom.geom_type == 'MultiPolygon':
            results.extend(geom.geoms)
        elif geom.geom_type == 'GeometryCollection':
            results.extend(split_out_all_multis(geom.geoms))
        else:
            raise NotImplementedError(geom.geom_type)

    return results

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

def do_difference(filename_a, files_to_remove, output_filename, min_area):
    print "Reading in {}".format(filename_a)
    with fiona.open(filename_a) as fpa:
        output_crs = fpa.crs

        data_a = [shape(x['geometry']) for x in fpa]

    geom_index = index.Index()
    polys_to_remove = []
    for filename in files_to_remove:
        print "Reading in {}".format(filename)
        with fiona.open(filename) as fpb:
            polys_to_remove.extend(shape(x['geometry']) for x in fpb)

    for pos, b_obj in enumerate(polys_to_remove):
        geom_index.insert(pos, b_obj.bounds)


    num_as = len(data_a)
    output_geoms = []
    for idx, a_geom in enumerate(data_a):
        sys.stdout.write("Looking at object {:,} of {:,}\r".format(idx, num_as))
        sys.stdout.flush()
        possible_bs = shapely.ops.cascaded_union([polys_to_remove[pos] for pos in geom_index.intersection(a_geom.bounds)])
        new_geom = a_geom.difference(possible_bs)
        output_geoms.append(new_geom)
    print "\n"

    output_geoms = split_out_all_multis(output_geoms)

    if min_area:
        output_geoms = [x for x in output_geoms if x.area >= min_area]

    print "Merging all geoms together..."
    output_geom = shapely.ops.cascaded_union(output_geoms)

    # split into companent shapes
    output_geoms = split_out_all_multis(output_geom)
    

    print "Writing output"
    with fiona.open(output_filename, 'w', 'ESRI Shapefile', crs=output_crs, schema={'geometry': 'Polygon', 'properties': {}}) as output_fp:
        for geom in output_geoms:
            output_fp.write({'properties': {}, 'geometry': mapping(geom)})

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--land")
    parser.add_argument("-r", "--remove", action="append")
    parser.add_argument("-a", "--min-area", default=None, required=False, type=float)
    parser.add_argument("-o", "--output")
    parser.add_argument("-q", "--quiet", default=False, action="store_true")

    args = parser.parse_args(argv)
    do_difference(args.land, args.remove, args.output, args.min_area)

if __name__ == '__main__':
    main(sys.argv[1:])
