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
import xlsxwriter
random.seed(0)
np.random.seed(0)

### spatial queue model
sys.path.insert(0, '..')
import model.queue_class_ce170 as sq_loop
import model.spatial_queue_array_add_storage_remain_special_node_reroute_rtt_change_queue_length as sq_vect


# In[11]:

frac = 1
### Read network and demand
case='fairfax'
bg_exist = 1 # 1 represents bg exists, 0 represents bg does not exist
nodes_df = pd.read_csv('traffic_inputs/{}/new_{}_nodes_tmp.csv'.format(case,case), float_precision = "round_trip")
links_df = pd.read_csv('traffic_inputs/{}/new_{}_links_tmp.csv'.format(case,case), float_precision = "round_trip")
#od_df = pd.read_csv('traffic_inputs/{}/{}_ods_day_new_tmp.csv'.format(case,case), float_precision = "round_trip")
#od_df['agent_id'] = np.arange(120000, 120000 + len(od_df))
### these are done for the vectorized implementation
if bg_exist == 1:
    background_od = pd.read_csv('traffic_inputs/{}/background_ods_day_for_Marin_new_change_marin_side_od.csv'.format(case,case), float_precision = "round_trip")
    background_od = background_od.sample(frac=frac)
    background_od.reset_index(drop = True, inplace = True)
    background_od['agent_id'] = np.arange(len(background_od))
    od_df = background_od.copy()
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':10741,'destin_nid':15434,'departure_time':0,'agent_id':200000}], ignore_index = True) # 6 a.m. arrive at 1100s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':10741,'destin_nid':15434,'departure_time':3600,'agent_id':200001}], ignore_index = True) # 7 a.m. arrive at 4700s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':10741,'destin_nid':15434,'departure_time':7200,'agent_id':200002}], ignore_index = True) # 8 a.m. arrive at 8300s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':10741,'destin_nid':15434,'departure_time':10800,'agent_id':200003}], ignore_index = True) # 9 a.m. arrive at 11800s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':7020,'destin_nid':15434,'departure_time':0,'agent_id':200004}], ignore_index = True) # 6 a.m. arrive at 1000s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':7020,'destin_nid':15434,'departure_time':3600,'agent_id':200005}], ignore_index = True) # 7 a.m. arrive at 4700s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':7020,'destin_nid':15434,'departure_time':7200,'agent_id':200006}], ignore_index = True) # 8 a.m. arrive at 8500s
    od_df = od_df.append([{'origin_nid_old':1,'destin_nid_old':1,'departure_hour':1,'departure_quarter':1,'origin_nid':7020,'destin_nid':15434,'departure_time':10800,'agent_id':200007}], ignore_index = True) # 9 a.m. arrive at 11900s

od_df = od_df[od_df['origin_nid']!=od_df['destin_nid']]
#od_df['agent_id'] = np.arange(len(od_df)) #record every o-d id

nodes_df['node_id'] = nodes_df['node_id'].astype(int)
print('# nodes {}, # links {}, # ods {}'.format(nodes_df.shape[0], links_df.shape[0], od_df.shape[0]))


# ### This is the vectorized simulation.

# In[12]:
global a1,a2,a3,a4,a5,a6,a7,a8
a1 =0; a2=0; a3 =0; a4=0; a5=0; a6 =0; a7 =0; a8 = 0

# count the number of evacuees that have successfully reach their destination
def arrival_counts_vect(t, simulation, save_path, save_path_1):
    arrival_cnts = np.sum((simulation.agents.agents['agent_status'] == -1) & (simulation.agents.agents['destin_nid'] == 15434))
    need_arrival_cnts = np.sum(simulation.agents.agents['destin_nid'] == 15434)
    arrival_cnts_total = np.sum(simulation.agents.agents['agent_status']==-1)
    need_arrival_cnts_total = simulation.agents.agents.shape[0]
    #print('At {} seconds, {}-{} evacuees successfully reached the destination'.format(t, arrival_cnts, need_arrival_cnts))
    #print('At {} seconds, {}-{} evacuees successfully reached the destination (total)'.format(t, arrival_cnts_total, need_arrival_cnts_total))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200000, 'agent_status'].values[0] == -1):
        global a1
        a1 +=1
        if a1 <=1:
            print('agent_id: 200000, reach the destination at {}'.format(t))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200001, 'agent_status'].values[0] == -1):
        global a2
        a2 +=1
        if a2 <=1:
            print('agent_id: 200001, reach the destination at {}'.format(t))    

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200002, 'agent_status'].values[0] == -1):
        global a3
        a3 +=1
        if a3 <=1:
            print('agent_id: 200002, reach the destination at {}'.format(t))


    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200003, 'agent_status'].values[0] == -1):
        global a4
        a4 +=1
        if a4 <=1:
            print('agent_id: 200003, reach the destination at {}'.format(t))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200004, 'agent_status'].values[0] == -1):
        global a5
        a5 +=1
        if a5 <=1:
            print('agent_id: 200004, reach the destination at {}'.format(t))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200005, 'agent_status'].values[0] == -1):
        global a6
        a6 +=1
        if a6 <=1:
            print('agent_id: 200005, reach the destination at {}'.format(t))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200006, 'agent_status'].values[0] == -1):
        global a7
        a7 +=1
        if a7 <=1:
            print('agent_id: 200006, reach the destination at {}'.format(t))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200007, 'agent_status'].values[0] == -1):
        global a8
        a8 +=1
        if a8 <=1:
            print('agent_id: 200007, reach the destination at {}'.format(t))

    if (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200007, 'agent_status'].values[0] == -1) & (simulation.agents.agents.loc[simulation.agents.agents['agent_id'] == 200003, 'agent_status'].values[0] == -1):
        return False


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

def write_all_link_outputs_vect(simulation, save_path):
    link_output = simulation.network.links.loc[
        simulation.network.links['link_type'].isin(['real', 'virtual']), 
        ['link_id', 'queue', 'run', 'undeparted', 'length', 'storage_remain', 'geometry','storage_add_times']].copy()

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

def write_link_enter_leave_df(simulation, save_path):
    link_enter_leave_df = simulation.network.link_enter_leave_df
    link_enter_leave_df.to_csv(save_path, index = False)


def write_loops(simulation, save_path):
    
    workbook = xlsxwriter.Workbook(save_path)
    worksheet = workbook.add_worksheet()
    row = 0

    for key in simulation.loops.keys():
        for item in simulation.loops[key]:
            col = 0
            row += 1
            worksheet.write(row-1,col,key)
            for item_ in item:
                col += 1
                worksheet.write(row-1,col,item_)

        
    workbook.close()


### initialize simulation
simulation_vect = sq_vect.Simulation()
simulation_vect.initialize_simulation(nodes_df, links_df, od_df)

### specify some parameters
scenario_name = '{}_vect'.format(case)
t_end = 3600 * 20

arrival_output_path = 'traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_bg_1_real_departure_time_total.csv'.format(case, scenario_name)
arrival_output_path_1 = 'traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_bg_1_real_departure_time_evacuation.csv'.format(case, scenario_name)



### run simulation and output results
with open(arrival_output_path, 'w') as t_stats_outfile:
    t_stats_outfile.write("t,arrival_count"+"\n")

with open(arrival_output_path_1, 'w') as t_stats_outfile:
    t_stats_outfile.write("t,arrival_count"+"\n")

# iterate through each time step
t_start_vect = time.time()
for t in range(t_end):
    # run the spatial-queue simulation for one step
    simulation_vect.run_one_step(t, reroute_frequency=10)

    if t%600 == 0:
        if bg_exist == 1:
            link_output_path = 'traffic_outputs/{}/with_bg/link_stats_add_srsn_reroute_rtt/l{}_at_{}_bg_1_real_departure_time.csv'.format(case, scenario_name, t)
            agent_output_path = 'traffic_outputs/{}/with_bg/agent_stats_add_srsn_reroute_rtt/{}_at_{}_bg_1_real_departure_time_agent.csv'.format(case, scenario_name, t)
            link_enter_leave_path = 'traffic_outputs/{}/with_bg/link_enter_leave_onlybg_frac{}/link_enter_leave_time_{}.csv'.format(case,frac,t)
        #node_output_path = 'traffic_outputs/berkeley/node_stats/n{}_at_{}.csv'.format(scenario_name, t)
        #write_link_outputs_vect(simulation_vect, link_output_path)
        #write_node_outputs(simulation_vect, node_output_path)
        #write_agent_evac_outputs_vect(simulation_vect, agent_output_path)
        #write_link_enter_leave_df(simulation_vect, link_enter_leave_path)
    # output time-step results every 100 seconds
    if t%100 == 0:
        if not arrival_counts_vect(t, simulation_vect, arrival_output_path,arrival_output_path_1):
            #write_loops(simulation_vect, 'traffic_outputs/{}/with_bg/loop_add_srsn/loops_add_srsn_reroute_rtt.xlsx'.format(case))
            #write_all_link_outputs_vect(simulation_vect, 'traffic_outputs/{}/with_bg/link_stats_add_srsn_reroute_rtt/l{}_at_{}_all_links.csv'.format(case, scenario_name, t))
            #write_link_enter_leave_df(simulation_vect, link_enter_leave_path)
            break

    #if t % 1000 == 0:
        #write_all_link_outputs_vect(simulation_vect, 'traffic_outputs/{}/with_bg/link_stats_add_srsn_reroute_rtt/l{}_at_{}_all_links.csv'.format(case, scenario_name, t))


print ("simulation completed")
t_end_vect = time.time()
print('Simulation took {}s'.format(t_end_vect - t_start_vect))
