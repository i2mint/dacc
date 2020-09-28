
# dacc
A declarative approach to data access object construction

The idea is to be able to specify a DAG (Directed Acyclic Graph) of data 
dependencies, and only have to retrieve or compute datas as they are needed. 

This is an older solution, that will soon be replaced with a more modern approach, 
involving properties and cached_properties...

## Example

Here is a full, and real, example of usage.

Here we tap into some website visitor data (in mongoDB) that has IP addresses for every visit, 
and use those to get approximate geo-coordinates for the visit.

```python
from ut.util.data_flow import DataFlow
from pymongo import MongoClient
import pygeoip
from pandas import DataFrame
from collections import Counter


traj_names = {
    'ip': 'IP',
    'date': 'date'
}

event_names = {
    'audience_volume': 'audience_volume',
    'broadcast_population_range': 'broadcast_population_range',
    'broadcast_hard_radius': 'broadcast_hard_radius'
}

ip_geo_data_filepath = '~/Data/geo/geoip/GeoLiteCity.dat'  # GeoIP.dat?

traj_mongo_db = 'fuak'
traj_mongo_collection = 'visits'

gi = pygeoip.GeoIP(ip_geo_data_filepath)

def get_location_info(ip):
    geo = gi.record_by_addr(ip)
    return {'lat': geo.get('latitude'),
            'lon': geo.get('longitude')}

ip_2_latlon = get_location_info
traj_data = MongoClient()[traj_mongo_db][traj_mongo_collection]

class TrajFeatBuilder(DataFlow):
    def __init__(self, ip_geo_data_filepath=ip_geo_data_filepath, **kwargs):
        params = dict()
        params['data_dependencies'] = {
            'ip_list': ['visitor_id'], 
            'ip_counts': ['ip_list'], 
            'latlon_counts': ['ip_counts']
        }
        params['data_makers'] = {k: params[k] for k in params['data_dependencies'].keys() if k in params.keys()}
        kwargs = dict(kwargs, **params)
        super(TrajFeatBuilder, self).__init__(**kwargs)

        self.ip_2_latlon = get_location_info
        self.traj_data = MongoClient()[traj_mongo_db][traj_mongo_collection]

    def get_features(self, **kwargs):
        visitor_id = kwargs.get('visitor_id', None)

        if visitor_id:
            ip_counts = self._ip_list_to_ip_counts(ip_list=self._visitor_id_to_ip_list(visitor_id=visitor_id))
            # ip_counts = self._visitor_id_to_ip_list(visitor_id=visitor_id)
            # ip_counts = Counter([x['ip'] for x in self.traj_data.find({'visitor_id': visitor_id},
            #                                                           fields={'_id': False, 'ip': True})])
            if len(ip_counts) == 0:
                return None
            else:
                location_counts = DataFrame(map(self.ip_2_latlon, ip_counts.keys()))
                location_counts['count'] = ip_counts.values()
                return {'visitor_id': visitor_id, 'location_counts': self._ip_counts_to_latlon_counts(ip_counts)}
        else:
            raise ValueError('Unknown traj format (should be a visitor_id)')

    def ip_list(self, visitor_id, **kwargs):
        return [x['ip'] for x in self.traj_data.find({'visitor_id': visitor_id},
                                                     fields={'_id': False, 'ip': True})]

    def ip_counts(self, ip_list, **kwargs):
        return Counter(ip_list)

    def latlon_counts(self, ip_counts, **kwargs):
        latlon_counts = DataFrame(map(self.ip_2_latlon, ip_counts.keys()))
        latlon_counts['count'] = ip_counts.values()
        return latlon_counts


```

Make the object:

```python
dflow = TrajFeatBuilder(verbose_level=10)

```

Get an `ip_list` for a given visitor

```python
dflow.get_data('ip_list', visitor_id='201411301840218052872011')
```

```
['86.73.225.225',
 '86.73.225.225',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '84.103.117.129',
 '86.73.225.248',
 '86.73.225.225',
 '86.73.225.225',
 '86.73.225.225',
 '86.73.225.225',
 '86.73.225.225',
 '86.73.225.225',
 '86.73.225.225']
```
Get a count of the locations coordinates where visitor was present.

```python
dflow.get_data('latlon_counts', visitor_id='201411301840218052872011')
```

|    |     lat |    lon |   count |
|---:|--------:|-------:|--------:|
|  0 | 48.9258 | 2.4453 |       1 |
|  1 | 48.9102 | 2.5532 |      12 |
|  2 | 48.9258 | 2.4453 |       9 |
