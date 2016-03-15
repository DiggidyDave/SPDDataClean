import plac

class DataItem(object):
    def __init__(self, headers, values):
        self.headers = headers
        self.values = values

        self['Latitude'] = round(float(self['Latitude']), 5)
        self['Longitude'] = round(float(self['Longitude']), 5)


    def __getitem__(self, value_name):
        # if string is passed, find index for that header and retrieve value for it
        # otherwise defer to default impl for list
        if isinstance(value_name, str):
            try:
                idx = self.headers.index(value_name)
                return self.values[idx]
            except:
                return None
        else:
            return list.__getitem__(self.values, value_name)

    def __setitem__(self, value_name, value):
        idx = self.headers.index(value_name)
        self.values[idx] = value

    def hundred_block_loc(self):    return self['Hundred Block Location']
    def lat(self):                  return self['Latitude']
    def lon(self):                  return self['Longitude']


class DataSet(object):
    def __init__(self, headers = None, items = None):
        self.headers = headers
        self.items = items or []

    def add_item(self, values):
        self.items.append(DataItem(self.headers, values))

def load_crime_data(csv_file):
    data = DataSet()
    with open(csv_file) as in_file:
        data.headers = in_file.readline().strip().split(',')
        for line in in_file.readlines():
            data.add_item(line.strip().split(","))

    return data

def clean_data(data):
    dedup_location_addrs(data)

def dedup_location_addrs(data):
    locs = {}
    dup_loc_count = 0
    dup_count = 0

    # Group incidents by lat/lon
    by_loc = {}
    num_locs = 0
    num_items = 0
    for item in data.items:
        num_items += 1
        lat_lon = (item.lat, item.lon)
        if not lat_lon in by_loc:
            by_loc[lat_lon] = []
            num_locs += 1
        by_loc[lat_lon].append(item)
    print("There are {0} total locations for {1} incidents.".format(num_locs, num_items))

    dup_count = 0
    duped_loc_count = 0
    for loc in by_loc:
        blocks = [incident.hundred_block_loc for incident in by_loc[loc]]
        if len(blocks) > 1:
            dup_count += len(blocks)
            duped_loc_count += 1

    print("There are {0} duped locations with {1} total incidents.".format(duped_loc_count, dup_count))



def main(data_file_in, data_file_out):
    data = load_crime_data(data_file_in)
    clean_data(data)

if __name__ == "__main__":
    plac.call(main)