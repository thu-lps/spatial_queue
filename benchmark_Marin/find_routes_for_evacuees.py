
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import random
import sys
random.seed(0)
np.random.seed(0)

### spatial queue model
sys.path.insert(0, '..')
import model.queue_class_ce170 as sq_loop
import model.spatial_queue_array_add_storage_remain_special_node_reroute_rtt_change_queue_length as sq_vect


# In[2]:


### Read network and demand
case='fairfax'
nodes_df = pd.read_csv('traffic_inputs/{}/new_{}_nodes_tmp.csv'.format(case,case), float_precision = "round_trip")
links_df = pd.read_csv('traffic_inputs/{}/new_{}_links_tmp.csv'.format(case,case), float_precision = "round_trip")
od_df = pd.read_csv('traffic_inputs/{}/{}_ods_day_new_tmp.csv'.format(case,case), float_precision = "round_trip")
#links_df.loc[links_df['link_id'].isin([15290,31970,7444,35285,15229,26277,11937,7153,12176,7143,58,18977,9668,12414]), 'lanes'] = 1
#links_df.loc[links_df['link_id'].isin([10578,8169,17954,34851,33134,36158,26795,37330,4774,7423,34554,31563,33888,4865]), 'lanes'] = links_df.loc[links_df['link_id'].isin([10578,8169,17954,34851,33134,36158,26795,37330,4774,7423,34554]), 'lanes'].apply(lambda x: max(2,x))
#links_df.loc[links_df['link_id'].isin([14449, 21564, 30429, 9688, 22980, 1408, 7470, 12936, 15644,9699, 22125]), 'lanes'] = 1
#links_df.loc[links_df['link_id'].isin([453,15382, 31975, 10368, 4969, 13113, 9924, 30445, 22430, 4456, 23103, 189, 15153, 17738, 11631, 6037, 17671, 12217, 178, 223, 8627, 14269, 30469, 232, 3728, 16782]), 'lanes'] = 2 # Route 6
od_df['agent_id'] = np.arange(120000, 120000 + len(od_df))
od_df.loc[:, 'departure_hour'] = 6
od_df.loc[:, 'departure_quarter'] = 0
od_df['departure_time'] = (od_df['departure_hour'] - 6) * 3600 + od_df['departure_quarter'] * 900
od_df = od_df[od_df['origin_nid']!=od_df['destin_nid']]
nodes_df['node_id'] = nodes_df['node_id'].astype(int)
print('# nodes {}, # links {}, # ods {}'.format(nodes_df.shape[0], links_df.shape[0], od_df.shape[0]))


# In[3]:


simulation_vect = sq_vect.Simulation()
simulation_vect.initialize_simulation(nodes_df, links_df, od_df)


# In[4]:


for t in [0]:
    simulation_vect.run_one_step(t, reroute_frequency=10)


# In[5]:


agents_routes_dict = simulation_vect.agents.agent_routes


# In[6]:


print(sum(simulation_vect.network.links['rtt'] - simulation_vect.network.links['fft']))


# In[7]:


node_uv_link_dict = dict(zip(zip(links_df['start_node_id'], links_df['end_node_id']), links_df['link_id']))


# In[8]:



# In[9]:


from tqdm import tqdm
agents_links_dict = {}
for agent_id in tqdm(agents_routes_dict):
    links_list = []
    routes = agents_routes_dict[agent_id]
    for node_u, node_v in routes.items():
        #link_id_tmp = links_df.loc[(links_df['start_node_id'] == node_u) & (links_df['end_node_id'] == node_v), 'link_id'].values[0]
        link_id_tmp = node_uv_link_dict.get((node_u, node_v))
        links_list.append(link_id_tmp)
    agents_links_dict[agent_id] = links_list


# In[10]:



# In[11]:


#agents_links_dict[120145]


# In[12]:


links_passed = list(agents_links_dict.values())
links_passed = sum(links_passed,[])


# In[13]:


unique, counts = np.unique(links_passed, return_counts=True)
links_passed_count = dict(zip(unique, counts))


# In[14]:


link_geometry_dict = dict(zip(links_df['link_id'], links_df['geometry']))
link_lanes_dict = dict(zip(links_df['link_id'], links_df['lanes']))


# In[15]:


#link_lanes_dict.get(22430)


# In[16]:


link_passed_df = pd.DataFrame()
link_passed_df['link_id'] = list(links_passed_count.keys())
link_passed_df['count'] = link_passed_df['link_id'].map(links_passed_count)
link_passed_df['lanes'] = link_passed_df['link_id'].map(link_lanes_dict)
link_passed_df['geometry'] = link_passed_df['link_id'].map(link_geometry_dict)


# In[17]:

# In[18]:


# In[19]:

# In[20]:


link_passed_df = link_passed_df[link_passed_df['lanes'] < 100]
link_passed_df.to_csv('./{}_evacuees_links_passed_count_new.csv'.format(case), index = False)


# In[21]:


link_passed_df1 = link_passed_df[link_passed_df['count'] >= 1195]
link_passed_df1.to_csv('./{}_evacuees_links_frequently_passed_count_new.csv'.format(case), index = False)

