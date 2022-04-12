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
#get_ipython().run_line_magic('matplotlib', 'inline')
random.seed(0)
np.random.seed(0)

### spatial queue model
sys.path.insert(0, '..')
import model.queue_class_ce170 as sq_loop
import model.spatial_queue_array as sq_vect
from tqdm import tqdm

# In[11]:


### Read network and demand
case='fairfax'
nodes_df = pd.read_csv('traffic_inputs/{}_nodes_new.csv'.format(case))
links_df = pd.read_csv('traffic_inputs/{}_links_new.csv'.format(case))
od_df = pd.read_csv('traffic_inputs/{}_ods_day.csv'.format(case))

### these are done for the vectorized implementation
if case == 'berkeley':
    osmid2nid_dict = {getattr(n, 'node_osmid'): getattr(n, 'node_id') for n in nodes_df.itertuples()}
    od_df['origin_nid'] = od_df['origin_osmid'].map(osmid2nid_dict)
    od_df['destin_nid'] = od_df['destin_osmid'].map(osmid2nid_dict)
if case == 'fairfax':
    background_od = pd.read_csv('traffic_inputs/{}_ods_background_new.csv'.format(case))
    background_od_1 = background_od.sample(frac = 0.5)
    od_df = pd.concat([od_df, background_od]).sample(frac=1)
    od_df['origin_nid'] = od_df['origin_node_id']
    od_df['destin_nid'] = od_df['destin_node_id']
    nodes_df['node_id'] = nodes_df['nid']
    nodes_df['node_osmid'] = None
    links_df['link_id'] = links_df['eid']
    links_df['start_node_id'] = links_df['nid_s']
    links_df['end_node_id'] = links_df['nid_e']
print('# nodes {}, # links {}, # ods {}'.format(nodes_df.shape[0], links_df.shape[0], od_df.shape[0]))


# ### This is the vectorized simulation.

# In[12]:


# count the number of evacuees that have successfully reach their destination
def arrival_counts_vect(t, simulation, save_path):
    arrival_cnts = np.sum(simulation.agents.agents['agent_status']==-1 & (simulation.agents.agents['destin_nid'] == 224223))
    print('At {} seconds, {} evacuees successfully reached the destination'.format(t, arrival_cnts))
    if arrival_cnts == simulation.agents.agents.shape[0]:
        print("all agents arrive at destinations at time {} seconds.".format(t))
        return False
    with open(save_path, 'a') as t_stats_outfile:
        t_stats_outfile.write("{},{}".format(t, arrival_cnts) + "\n")
    return True

# write a csv file that contains the numbers of queuing and running vehicles on each link
def write_link_outputs_vect(simulation, save_path):
    link_output = simulation.network.links.loc[
        simulation.network.links['link_type'].isin(['real', 'virtual']), 
        ['link_id', 'queue', 'run', 'undeparted', 'length', 'geometry']].copy()
    link_output = link_output[
        (link_output['queue']>0) | (link_output['run']>0)
        | (link_output['undeparted']>0)
    ]
    link_output.to_csv(save_path, index=False)

print('start initial simulation')
### initialize simulation
simulation_vect = sq_vect.Simulation()
simulation_vect.initialize_simulation(nodes_df, links_df, od_df)
print('finish initial simulation')
### specify some parameters
scenario_name = '{}_vect'.format(case)
t_end = 7201
arrival_output_path = 'traffic_outputs/{}/t_stats/arrivals_{}.csv'.format(case, scenario_name)

### run simulation and output results
with open(arrival_output_path, 'w') as t_stats_outfile:
    t_stats_outfile.write("t,arrival_count"+"\n")

# iterate through each time step
t_start_vect = time.time()
for t in range(t_end):
    print(t)
    # run the spatial-queue simulation for one step
    simulation_vect.run_one_step(t, reroute_frequency=None)

    # output time-step results every 100 seconds
    if t%100 == 0:
        if not arrival_counts_vect(t, simulation_vect, arrival_output_path):
            break
        link_output_path = 'traffic_outputs/{}/link_stats/l{}_at_{}.csv'.format(case, scenario_name, t)
        #node_output_path = 'traffic_outputs/berkeley/node_stats/n{}_at_{}.csv'.format(scenario_name, t)
        write_link_outputs_vect(simulation_vect, link_output_path)
        #write_node_outputs(simulation_vect, node_output_path)

print ("simulation completed")
t_end_vect = time.time()
print('Simulation took {}s'.format(t_end_vect - t_start_vect))




