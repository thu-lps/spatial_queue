import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString
#把bg的终点换成虚拟点，增加node,增加link
ods_df = pd.read_csv('fairfax_ods_background.csv',float_precision="round_trip")
nodes = pd.read_csv('fairfax_nodes.csv',float_precision="round_trip")
link_data = pd.read_csv('fairfax_links.csv',float_precision="round_trip")

nodes_fairfax = pd.read_csv('fairfax_nodes_from_bay_area.csv',float_precision="round_trip")
nodes_fairfax = nodes_fairfax[['nid','osmid','lon','lat']]
nodes_fairfax['type'] = 'real'
print(nodes_fairfax.nid.max())

#print(link_data.head())
### add virtual nodes for destination_nid of background od
virtual_destin_nodes_df = nodes.loc[nodes['nid'].isin(np.unique(ods_df['destin_node_id']))].copy()
max_node_id = max(nodes['nid']) + 1
virtual_destin_nodes_df['nid'] = virtual_destin_nodes_df['nid'].apply(lambda x: int(x+max_node_id))


#print(virtual_destin_nodes_df.head())
nodes = pd.concat([nodes, virtual_destin_nodes_df])
nodes.to_csv('./fairfax_nodes_new.csv', header = True, index = False)

### add virtual links between real destination node and virtual detination node
virtual_destin_links_df = virtual_destin_nodes_df[['nid', 'lon', 'lat']].copy()
virtual_destin_links_df['nid_s'] = virtual_destin_links_df['nid'].apply(lambda x: int(x - max_node_id)) ### remove the 'vn_' from node id        
virtual_destin_links_df['nid_e'] = virtual_destin_links_df['nid']
virtual_destin_links_df['eid'] = virtual_destin_links_df['nid'].apply(lambda x: int(x+1e6))        
virtual_destin_links_df['type'] = 'vl_out'
virtual_destin_links_df['geometry'] = virtual_destin_links_df.apply(lambda e: LineString([(e['lon'], e['lat']), (e['lon'] + 0.00001, e['lat'] + 0.00001)]), axis = 1) 
virtual_destin_links_df['length'] = 1000
virtual_destin_links_df['maxmph'] = 1000
virtual_destin_links_df['lanes'] = 1e8
virtual_destin_links_df['capacity'] = 1e8
virtual_destin_links_df['fft'] = 0.1
virtual_destin_links_df['osmid'] = -1

link_data = pd.concat([link_data, virtual_destin_links_df[link_data.columns]])
#link_data['eid'] = np.arange(len(link_data))
link_data.to_csv('./fairfax_links_new.csv', header = True, index = False)


for i in range(len(ods_df)):
	if ods_df['destin_node_id'][i] in nodes['nid'].values:
		#print(ods_df['destin_node_id'][i])
		ods_df['destin_node_id'][i] = int(ods_df['destin_node_id'][i] + max_node_id)

ods_df.to_csv('./fairfax_ods_background_new.csv', header = True, index = False)
