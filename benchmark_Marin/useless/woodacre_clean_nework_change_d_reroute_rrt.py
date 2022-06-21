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
import model.spatial_queue_array_reroute_rtt as sq_vect


# In[11]:


### Read network and demand
case='woodacre'
bg_exist = 1 # 1 represents bg exists, 0 represents bg does not exist
nodes_df = pd.read_csv('traffic_inputs/{}/new_{}_nodes_tmp.csv'.format(case,case), float_precision = "round_trip")
links_df = pd.read_csv('traffic_inputs/{}/new_{}_links_tmp.csv'.format(case,case), float_precision = "round_trip")
od_df = pd.read_csv('traffic_inputs/{}/{}_ods_day_new_tmp.csv'.format(case,case), float_precision = "round_trip")
od_df['agent_id'] = np.arange(120000, 120000 + len(od_df))
### these are done for the vectorized implementation
if bg_exist == 1:
    special_nodes = {'first_priority':[], 'second_priority':[]}
    background_od = pd.read_csv('traffic_inputs/{}/background_ods_day_for_Marin_new_change_marin_side_od.csv'.format(case,case), float_precision = "round_trip")
    background_od = background_od.sample(frac=1)
    background_od['agent_id'] = np.arange(len(background_od))
    od_df = pd.concat([od_df, background_od]).sample(frac=1)
od_df.loc[:, 'departure_hour'] = od_df.loc[:, 'departure_hour'].fillna(6)
od_df.loc[:, 'departure_quarter'] = od_df.loc[:, 'departure_quarter'].fillna(0)

od_df['departure_time'] = (od_df['departure_hour'] - 6) * 3600 + od_df['departure_quarter'] * 900
od_df = od_df[od_df['origin_nid']!=od_df['destin_nid']]
#od_df['agent_id'] = np.arange(len(od_df)) #record every o-d id

nodes_df['node_id'] = nodes_df['node_id'].astype(int)
print('# nodes {}, # links {}, # ods {}'.format(nodes_df.shape[0], links_df.shape[0], od_df.shape[0]))





# count the number of evacuees that have successfully reach their destination
def arrival_counts_vect(t, simulation, save_path, save_path_1):
    arrival_cnts = np.sum((simulation.agents.agents['agent_status'] == -1) & (simulation.agents.agents['destin_nid'] == 15434))
    need_arrival_cnts = np.sum(simulation.agents.agents['destin_nid'] == 15434)
    arrival_cnts_total = np.sum(simulation.agents.agents['agent_status']==-1)
    need_arrival_cnts_total = simulation.agents.agents.shape[0]
    print('At {} seconds, {}-{} evacuees successfully reached the destination'.format(t, arrival_cnts, need_arrival_cnts))
    print('At {} seconds, {}-{} evacuees successfully reached the destination (total)'.format(t, arrival_cnts_total, need_arrival_cnts_total))
    if arrival_cnts_total == need_arrival_cnts_total:
        print("all agents arrive at destinations at time {} seconds.".format(t))
        return False
    with open(save_path, 'a') as t_stats_outfile:
        t_stats_outfile.write("{},{}".format(t, arrival_cnts_total) + "\n")
    with open(save_path_1, 'a') as t_stats_outfile:
        t_stats_outfile.write("{},{}".format(t, arrival_cnts) + "\n")
    return True

# write a csv file that contains the numbers of queuing and running vehicles on each link
def write_link_outputs_vect(simulation, save_path):
    link_output = simulation.network.links.loc[
        simulation.network.links['link_type'].isin(['real', 'virtual']), 
        ['link_id', 'queue', 'run', 'undeparted', 'length', 'storage_remain', 'geometry']].copy()
    link_output = link_output[
        (link_output['queue']>0) | (link_output['run']>0)
        | (link_output['undeparted']>0)
    ]
    link_output.to_csv(save_path, index=False)

def write_agent_evac_outputs_vect(simulation, save_path):
    agent_output = simulation.agents.agents.loc[:, ['agent_id','current_link','next_link', 'current_link_enter_time', 'agent_status', 'origin_nid', 'destin_nid']].copy()
    link_info = simulation.network.links.loc[
        simulation.network.links['link_type'].isin(['real', 'virtual']), 
        ['link_id','storage_remain']].copy()
    agent_output = pd.merge(left = agent_output, right = link_info, how = 'left', left_on = 'current_link', right_on = 'link_id')
    agent_output = agent_output[['agent_id','current_link','next_link', 'current_link_enter_time', 'agent_status', 'origin_nid', 'destin_nid', 'storage_remain']]
    agent_output = agent_output.rename(columns = {'storage_remain': 'current_link_storage_remain'})

    agent_output = pd.merge(left = agent_output, right = link_info, how = 'left', left_on = 'next_link', right_on = 'link_id')
    agent_output = agent_output[['agent_id','current_link','next_link', 'current_link_enter_time', 'agent_status', 'origin_nid', 'destin_nid', 'current_link_storage_remain', 'storage_remain']]
    agent_output = agent_output.rename(columns = {'storage_remain': 'next_link_storage_remain'})

    agent_output = agent_output[agent_output['agent_status'] != -1]
    agent_output.to_csv(save_path, index = False)

### initialize simulation
simulation_vect = sq_vect.Simulation()
simulation_vect.initialize_simulation(nodes_df, links_df, od_df)

### specify some parameters
scenario_name = '{}_vect'.format(case)
t_end = 3600 * 20
if bg_exist == 1:
    arrival_output_path = 'traffic_outputs/{}/with_bg/t_stats_reroute_rtt/arrivals_{}_bg_1_real_departure_time_total.csv'.format(case, scenario_name)
    arrival_output_path_1 = 'traffic_outputs/{}/with_bg/t_stats_reroute_rtt/arrivals_{}_bg_1_real_departure_time_evacuation.csv'.format(case, scenario_name)
else:
    arrival_output_path = 'traffic_outputs/{}/no_bg/t_stats_reroute_rtt/arrivals_{}_bg_1_real_departure_time.csv'.format(case, scenario_name)


### run simulation and output results
with open(arrival_output_path, 'w') as t_stats_outfile:
    t_stats_outfile.write("t,arrival_count"+"\n")

with open(arrival_output_path_1, 'w') as t_stats_outfile:
    t_stats_outfile.write("t,arrival_count"+"\n")

# iterate through each time step
t_start_vect = time.time()
for t in range(t_end):
    # run the spatial-queue simulation for one step
    simulation_vect.run_one_step(t, reroute_frequency=1800)

    # output time-step results every 100 seconds
    if t%100 == 0:
        if not arrival_counts_vect(t, simulation_vect, arrival_output_path,arrival_output_path_1):
            break

        link_output_path = 'traffic_outputs/{}/with_bg/link_stats_reroute_rtt/l{}_at_{}_bg_1_real_departure_time.csv'.format(case, scenario_name, t)
        agent_output_path = 'traffic_outputs/{}/with_bg/agent_stats_reroute_rtt/{}_at_{}_bg_1_real_departure_time_agent.csv'.format(case, scenario_name, t)

        #node_output_path = 'traffic_outputs/berkeley/node_stats/n{}_at_{}.csv'.format(scenario_name, t)
        write_link_outputs_vect(simulation_vect, link_output_path)
        #write_node_outputs(simulation_vect, node_output_path)
        write_agent_evac_outputs_vect(simulation_vect, agent_output_path)

print ("simulation completed")
t_end_vect = time.time()
print('Simulation took {}s'.format(t_end_vect - t_start_vect))
