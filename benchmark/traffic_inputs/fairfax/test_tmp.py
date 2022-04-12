import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString
#把bg的终点换成虚拟点，增加node,增加link
#ods_df = pd.read_csv('fairfax_ods_day_new.csv')
#ods_df['destin_nid'] = 99885

#ods_df.to_csv('fairfax_ods_day_new_tmp.csv', header = True, index = False)

link_data = pd.read_csv('new_fairfax_links.csv')
print(link_data.loc[link_data['start_node_id'] == 95155, ['link_id', 'length','lanes','type','capacity', 'end_node_id', 'maxmph']])
#print(link_data.loc[link_data['link_id'].isin([323900, 285161, 323870, 324489, 91169, 248566, 129930, 297982, 323957, 323957, 323859, 259105, 248650, 323842, 323804, 247581, 309240, 323803, 268800, 281398]), ['link_id', 'length','lanes','type','capacity','start_node_id', 'end_node_id']])
#link_data['storage'] = link_data['length'] * link_data['lanes']
#print(max(link_data.loc[link_data['link_id'].isin([323900, 285161, 323870, 324489, 91169, 248566, 129930, 297982, 323957, 323957, 323859, 259105, 248650, 323842, 323804, 247581, 309240, 323803, 268800, 281398]), 'storage']))
#print((link_data.loc[link_data['link_id'].isin([399960,48855,252309,399767,257056,257028,263921,291741,273032,273042,248037,107291,7872]), 'storage']))
#print(link_data.loc[link_data['link_id'] == 250524, ['link_id', 'length','lanes','type','capacity','start_node_id', 'end_node_id']])
#print(link_data.loc[link_data['lanes'] == 18, ['link_id', 'length','lanes','type','capacity','start_node_id', 'end_node_id']])