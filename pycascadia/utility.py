def region_to_str(region):
    return '/'.join(map(str, region))

def min_regions(region1, region2):
    """Returns the smaller of the two regions (i.e. the intersection)"""
    return [max(region1[0], region2[0]), min(region1[1], region2[1]), max(region1[2], region2[2]), min(region1[3], region2[3])]

def is_region_valid(region):
    if region[1] < region[0] or region[3] < region[2]:
        return False
    else:
        return True

def read_fnames(input_txt):
    """Reads filenames from text file, removing empty lines and training newlines"""
    with open(input_txt, 'r') as fp:
        lines = [fname.strip() for fname in fp.readlines() if fname != '\n']

    return lines
