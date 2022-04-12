#!/usr/bin/env python
# coding: utf-8

# ### Benchmark
# compare the loop and vectorized implementation.
# 
#   * Loop through each node: [model/queue_class_ce170.py](model/queue_class_ce170.py)
#   * Vectorized: [model/spatial_queue_array.py](model/spatial_queue_array.py)

# In[4]:


import sys
import time 
import random
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
random.seed(0)
np.random.seed(0)

### spatial queue model
sys.path.insert(0, '..')
import model.queue_class_ce170 as sq_loop
import model.spatial_queue_array as sq_vect


# In[11]:


### Read network and demand
case='fairfax'
bg_exist = 1 # 1 represents bg exists, 0 represents bg does not exist
nodes_df = pd.read_csv('traffic_inputs/{}/new_{}_nodes.csv'.format(case,case))
links_df = pd.read_csv('traffic_inputs/{}/new_{}_links.csv'.format(case,case))
#od_df = pd.read_csv('traffic_inputs/{}/{}_ods_day_new.csv'.format(case,case))

link_nid_dict = {(getattr(link, 'start_node_id'), getattr(link, 'end_node_id')): getattr(link, 'link_id') for link in links_df.itertuples()}
if ((95155, 99085), 250526) in link_nid_dict.items():
    print('True')

print(len(links_df))

'''
od_df = pd.DataFrame()
### these are done for the vectorized implementation
if bg_exist == 1:
    special_nodes = {'first_priority':[], 'second_priority':[]}
    background_od = pd.read_csv('traffic_inputs/{}/{}_ods_background_new.csv'.format(case,case))
    background_od = background_od.sample(frac=1)
    od_df = pd.concat([od_df, background_od]).sample(frac=1)
#od_df.loc[:, 'departure_hour'] = od_df.loc[:, 'departure_hour'].fillna(6)
#od_df.loc[:, 'departure_quarter'] = od_df.loc[:, 'departure_quarter'].fillna(0)

#od_df['departure_time'] = (od_df['departure_hour'] - 6) * 3600 + od_df['departure_quarter'] * 900
od_df = od_df[od_df['origin_nid']!=od_df['destin_nid']]
od_df['agent_id'] = np.arange(len(od_df))
nodes_df['node_id'] = nodes_df['new_nid'].astype(int)
print('# nodes {}, # links {}, # ods {}'.format(nodes_df.shape[0], links_df.shape[0], od_df.shape[0]))


# ### This is the vectorized simulation.

# In[12]:




### initialize simulation
simulation_vect = sq_vect.Simulation()
simulation_vect.initialize_simulation(nodes_df, links_df, od_df)
'''
