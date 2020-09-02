#!/usr/bin/env python
# coding: utf-8

import os
import gc
import sys
import time 
import random
import logging 
import numpy as np
import pandas as pd 
from ctypes import c_double
import scipy.io as sio
import geopandas as gpd
from shapely.wkt import loads
from shapely.geometry import Point
import scipy.sparse as ssparse
import multiprocessing
from multiprocessing import Pool
from scipy.stats import truncnorm
### dir
home_dir = '.' # os.environ['HOME']+'/spatial_queue'
work_dir = '.' # os.environ['WORK']+'/spatial_queue'
scratch_dir = 'projects/butte_osmnx/simulation_outputs' # os.environ['OUTPUT_FOLDER']
### user
sys.path.insert(0, home_dir+'/..')
from sp import interface
import util.haversine as haversine
from queue_class import Node, Link, Agent

# random.seed(1)
# np.random.seed(1)

### distance to fire starting point
def cnt_veh_in_fire(t_now, veh_loc=None, fire_df=None):
    [veh_lon, veh_lat] = zip(*veh_loc)
    in_fire_dict = dict()
    for fire in fire_df.itertuples():
        if t_now >= getattr(fire, 'start_time'):
            fire_start_lon, fire_start_lat = getattr(fire, 'lon'), getattr(fire, 'lat')
            fire_speed = getattr(fire, 'fire_speed')
            in_fire_dict[getattr(fire, 'start_zone')] = haversine.haversine(np.array(veh_lat), np.array(veh_lon), fire_start_lat, fire_start_lon) < fire_speed * t_now
    in_fire_df = pd.DataFrame(in_fire_dict)
    in_fire_cnt = np.sum(in_fire_df.max(axis=1))
    return in_fire_cnt

def road_to_fire_dist(link_id_dict, fire_df):
    link_geom_df = pd.DataFrame([[link_id, link.geometry] for link_id, link in link_id_dict.items()], columns=['link_id', 'geometry'])
    link_geom_gdf = gpd.GeoDataFrame(link_geom_df, crs='epsg:4326', geometry=link_geom_df['geometry']).to_crs('epsg:3857')
    fire_gdf = gpd.GeoDataFrame(fire_df, crs='epsg:4326', geometry=[Point(xy) for xy in zip(fire_df.lon, fire_df.lat)]).to_crs('epsg:3857')
    link_fire_dist_dict = dict()
    for link in link_geom_gdf.itertuples():
        link_fire_dist = []
        for fire in fire_gdf.itertuples():
            start_lon_proj, start_lat_proj, end_lon_proj,  end_lat_proj  = getattr(link, 'geometry').coords[0][0], getattr(link, 'geometry').coords[0][1], getattr(link, 'geometry').coords[-1][0], getattr(link, 'geometry').coords[-1][1]
            l13 = np.vstack((getattr(fire, 'geometry').coords[0][0] - start_lon_proj, getattr(fire, 'geometry').coords[0][1] - start_lat_proj)).T
            l23 = np.vstack((getattr(fire, 'geometry').coords[0][0] - end_lon_proj, getattr(fire, 'geometry').coords[0][1] - end_lat_proj)).T
            l12 = (end_lon_proj - start_lon_proj, end_lat_proj - start_lat_proj)
            l21 = (start_lon_proj - end_lon_proj, start_lat_proj - end_lat_proj)
            ### line distance
            line_dist = np.abs(np.matmul(l13, (l12[-1], -l12[0]))) / np.linalg.norm(l12)
            ### start_dist_array
            start_node_distance = np.linalg.norm(l13, axis=1)
            start_node_angle = np.matmul(l13, l12)
            ### end_dist_array
            end_node_distance = np.linalg.norm(l23, axis=1)
            end_node_angle = np.matmul(l23, l21)
            point_line_dist = np.where(start_node_angle<0, start_node_distance,
                                        np.where(end_node_angle<0, end_node_distance, line_dist))
            link_fire_dist.append(point_line_dist)
        link_fire_dist_dict[getattr(link, 'link_id')] = np.round(np.min(link_fire_dist),1)
    return link_fire_dist_dict

# ### distance to fire frontier
# def fire_frontier_distance(fire_frontier, veh_loc, t):
#     [veh_lon, veh_lat] = zip(*veh_loc)
#     if t>=np.max(fire_frontier['t']):
#         fire_frontier_now = fire_frontier.loc[fire_frontier['t'].idxmax(), 'geometry']
#         veh_fire_dist = haversine.point_to_vertex_dist(veh_lon, veh_lat, fire_frontier_now)
#     else:
#         t_before = np.max(fire_frontier.loc[fire_frontier['t']<=t, 't'])
#         t_after = np.min(fire_frontier.loc[fire_frontier['t']>t, 't'])
#         fire_frontier_before = fire_frontier.loc[fire_frontier['t']==t_before, 'geometry'].values[0]
#         fire_frontier_after = fire_frontier.loc[fire_frontier['t']==t_after, 'geometry'].values[0]
#         veh_fire_dist_before = haversine.point_to_vertex_dist(veh_lon, veh_lat, fire_frontier_before)
#         veh_fire_dist_after = haversine.point_to_vertex_dist(veh_lon, veh_lat, fire_frontier_after)
#         veh_fire_dist = veh_fire_dist_before * (t_after-t)/(t_after-t_before) + veh_fire_dist_after * (t-t_before)/(t_after-t_before)
#     return np.mean(veh_fire_dist), np.sum(veh_fire_dist<0)
### numbers of vehicles that have left the evacuation zone / buffer distance
def outside_polygon(evacuation_zone, evacuation_buffer, veh_loc):
    [veh_lon, veh_lat] = zip(*veh_loc)
    evacuation_zone_dist = haversine.point_to_vertex_dist(veh_lon, veh_lat, evacuation_zone)
    evacuation_buffer_dist = haversine.point_to_vertex_dist(veh_lon, veh_lat, evacuation_buffer)
    return np.sum(evacuation_zone_dist>0), np.sum(evacuation_buffer_dist>0)

def network(network_file_edges=None, network_file_nodes=None, simulation_outputs=None, cf_files=[], scen_nm=''):
    # logger = logging.getLogger("butte_evac")

    links_df0 = pd.read_csv(work_dir + network_file_edges)
    ### contraflow
    if len(cf_files)>0:
        ### read contraflow links
        cf_links = []
        for cf_file in cf_files:
            cf_link_df = pd.read_csv(work_dir + cf_file)
            cf_links.append(cf_link_df)
        cf_links_df = pd.concat(cf_links)
        ### along counterflow direction
        cf_links_id = cf_links_df.loc[cf_links_df['along']==1, 'edge_id_igraph']
        links_df0['lanes'] = np.where(links_df0['edge_id_igraph'].isin(cf_links_id), links_df0['lanes']*2, links_df0['lanes'])
        ### opposite counterflow direction
        opcf_links_id = cf_links_df.loc[cf_links_df['along']==0, 'edge_id_igraph']
        links_df0['lanes'] = np.where(links_df0['edge_id_igraph'].isin(opcf_links_id), 0, links_df0['lanes'])
        links_df0['maxmph'] = np.where(links_df0['edge_id_igraph'].isin(opcf_links_id), 0.000001, links_df0['maxmph'])

    links_df0['fft'] = links_df0['length']/links_df0['maxmph']*2.237
    links_df0['capacity'] = 1900*links_df0['lanes']
    links_df0 = links_df0[['eid', 'nid_s', 'nid_e', 'lanes', 'capacity', 'maxmph', 'fft', 'length', 'geometry']]
    links_df0.to_csv(scratch_dir + simulation_outputs + '/modified_network_edges.csv', index=False)
    # sys.exit(0)

    nodes_df0 = pd.read_csv(work_dir + network_file_nodes)

    ### Convert to mtx
    # wgh = links_df0['fft']
    # row = links_df0['nid_s']
    # col = links_df0['nid_e']
    # assert max(np.max(row)+1, np.max(col)+1) == nodes_df0.shape[0], 'nodes and links dimension do not match, row {}, col {}, nodes {}'.format(np.max(row), np.max(col), nodes_df0.shape[0])
    # g_coo = ssparse.coo_matrix((wgh, (row, col)), shape=(nodes_df0.shape[0], nodes_df0.shape[0]))
    # logging.info("({}, {}), {}".format(g_coo.shape[0], g_coo.shape[1], len(g_coo.data)))
    # sio.mmwrite(scratch_dir + simulation_outputs + '/network_sparse_{}.mtx'.format(scen_nm), g_coo)
    # g_coo = sio.mmread(absolute_path+'/outputs/network_sparse.mtx'.format(folder))
    # g = interface.readgraph(bytes(scratch_dir + simulation_outputs + '/network_sparse_{}.mtx'.format('tabu'), encoding='utf-8'))
    g = interface.from_dataframe(links_df0, 'nid_s', 'nid_e', 'fft')

    ### Create link and node objects
    nodes = []
    links = []
    for row in nodes_df0.itertuples():
        real_node = Node(getattr(row, 'nid'), getattr(row, 'lon'), getattr(row, 'lat'), 'real', getattr(row, 'osmid'))
        virtual_node = real_node.create_virtual_node()
        virtual_link = real_node.create_virtual_link()
        nodes.append(real_node)
        nodes.append(virtual_node)
        links.append(virtual_link)
    for row in links_df0.itertuples():
        real_link = Link(getattr(row, 'eid'), getattr(row, 'lanes'), getattr(row, 'length'), getattr(row, 'fft'), getattr(row, 'capacity'), 'real', getattr(row, 'nid_s'), getattr(row, 'nid_e'), getattr(row, 'geometry'))
        links.append(real_link)

    return g, nodes, links


def demand(nodes_osmid_dict, dept_time_df=None, demand_files=None, tow_pct=0, phase_tdiff=None, reroute_pct=0):
    # logger = logging.getLogger("butte_evac")

    all_od_list = []
    for demand_file in demand_files:
        od = pd.read_csv(work_dir + demand_file)
        ### transform OSM based id to graph node id
        od['origin_nid'] = od['origin_osmid'].apply(lambda x: nodes_osmid_dict[str(x)])
        od['destin_nid'] = od['destin_osmid'].apply(lambda x: nodes_osmid_dict[x])
        ### assign agent id
        if 'agent_id' not in od.columns: od['agent_id'] = np.arange(od.shape[0])
        ### assign departure time. dept_time_std == 0 --> everyone leaves at the same time
        od = od.merge(dept_time_df, how='left', on='evac_zone')
        ### assign vehicle length
        od['veh_len'] = np.random.choice([8, 18], size=od.shape[0], p=[1-tow_pct, tow_pct])
        ### assign rerouting choice
        od['gps_reroute'] = np.random.choice([0, 1], size=od.shape[0], p=[1-reroute_pct, reroute_pct])
        all_od_list.append(od)

    all_od = pd.concat(all_od_list, sort=False, ignore_index=True)
    all_od = all_od.sample(frac=1).reset_index(drop=True) ### randomly shuffle rows
    logging.info('total numbers of agents from file {}'.format(all_od.shape))
    # all_od = all_od.iloc[0:3000].copy()
    logging.info('total numbers of agents taken {}'.format(all_od.shape))

    agents = []
    for row in all_od.itertuples():
        agents.append(Agent(getattr(row, 'agent_id'), getattr(row, 'origin_nid'), getattr(row, 'destin_nid'), getattr(row, 'dept_time'), getattr(row, 'veh_len'), getattr(row, 'gps_reroute')))    
    return agents

def map_sp(agent_id):
    subp_agent = agent_id_dict[agent_id]
    subp_status, subp_route = subp_agent.get_path(g=g)
    return (agent_id, subp_status, subp_route)

def route(scen_nm='', who=None):
    # logger = logging.getLogger("butte_evac")

    ### Find shortest pathes
    t_odsp_0 = time.time()
    if who=='all':
        map_agent = [k for k, v in agent_id_dict.items() if (v.cle != None)]
    elif who=='gps':
        map_agent = [k for k, v in agent_id_dict.items() if (v.cle != None) and (v.gps_reroute == True)]
    else:
        print('Unknown routing partition')
        sys.exit(0)

    ### Build a pool
    # process_count = 3# int(os.environ['OMP_NUM_THREADS'])
    # pool = Pool(processes=process_count)
    # res = pool.imap_unordered(map_sp, map_agent)
    ### Close the pool
    # pool.close()
    # pool.join()
    # cannot_arrive = 0

    ### no multiprocessing
    res = [map_sp(agent_id) for agent_id in map_agent]
    cannot_arrive = 0

    for (agent_id, subp_status, subp_route) in res:
        agent_id_dict[agent_id].find_route = subp_status
        if subp_status=='n_a': 
            ### still keep the route. Remove the agent when it reaches the closed link
            cannot_arrive += 1
            print(agent_id_dict[agent_id].origin_nid, agent_id_dict[agent_id].destin_nid)
            sys.exit(0)
        else:
            agent_id_dict[agent_id].route_igraph = subp_route
    t_odsp_1 = time.time()

    if cannot_arrive>0: logging.info('{} out of {} cannot arrive'.format(cannot_arrive, len(agent_id_dict)))
    return t_odsp_1-t_odsp_0, len(map_agent)

def link_model_worker(arg):
    link, t = arg
    link.run_link_model(t, agent_id_dict=agent_id_dict)

def node_model_worker(arg):
    node_id, t = arg
    node = node_id_dict[node_id]
    node_move, traffic_counter, agent_update_dict, link_update_dict = node.run_node_model(t, node_id_dict=node_id_dict, link_id_dict=link_id_dict, agent_id_dict=agent_id_dict, node2link_dict=node2link_dict)
    return (node_move, traffic_counter, agent_update_dict, link_update_dict)

def main(random_seed=None, fire_speed=None, dept_time_id=None, dept_time_df=None, tow_pct=None, hh_veh=None, reroute_pct=0, phase_tdiff=None, counterflow=None, fs=None, fire_df=None):
    ### logging and global variables

    global g, agent_id_dict, node_id_dict, link_id_dict, node2link_dict
    fitness = 0
    
    multiprocessing_flag = False
    reroute_freq = 10 ### sec
    link_time_lookback_freq = 20 ### sec
    network_file_edges = '/projects/butte_osmnx/network_inputs/butte_ctm_edges_sim_virtual.csv'
    network_file_nodes = '/projects/butte_osmnx/network_inputs/butte_ctm_nodes_sim_virtual.csv'
    demand_files = ["/projects/butte_osmnx/demand_inputs/ctm_od_virtual.csv"]
    simulation_outputs = '' ### scratch_folder
    if counterflow:
        cf_files = []
    else:
        cf_files = []

    scen_nm = "fs{}_dt".format(fs)+"-".join([str(x) for x in dept_time_df['dept_time'].values.tolist()])
    # logger = logging.getLogger("butte_evac")
    logging.basicConfig(filename=scratch_dir+simulation_outputs+'/log/{}.log'.format(scen_nm), filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO, force=True)
    logging.info(scen_nm)

    ### network
    g, nodes, links = network(
        network_file_edges = network_file_edges, network_file_nodes = network_file_nodes,
        simulation_outputs = simulation_outputs, cf_files = cf_files, scen_nm = scen_nm)
    nodes_osmid_dict = {node.osmid: node.id for node in nodes if node.type=='real'}
    node2link_dict = {(link.start_nid, link.end_nid): link.id for link in links}
    link_id_dict = {link.id: link for link in links}
    node_id_dict = {node.id: node for node in nodes}
    for link_id, link in link_id_dict.items():
        node_id_dict[link.start_nid].out_links.append(link_id)
        node_id_dict[link.end_nid].in_links[link_id] = None
    for node_id, node in node_id_dict.items():
        node.calculate_straight_ahead_links(node_id_dict=node_id_dict, link_id_dict=link_id_dict)
    
    ### demand
    evacuation_zone_gdf = gpd.read_file(work_dir+'/projects/butte_osmnx/demand_inputs/digitized_evacuation_zone/digitized_evacuation_zone.shp')
    evacuation_zone_gdf = evacuation_zone_gdf.loc[evacuation_zone_gdf['id']<=14].copy()
    evacuation_zone = evacuation_zone_gdf['geometry'].unary_union
    evacuation_buffer = evacuation_zone_gdf.to_crs('epsg:3857').buffer(1609).to_crs('epsg:4326').unary_union
    logging.info('Evacuation zone is {} km2, considering 1mile buffer it is {} km2'.format(evacuation_zone_gdf.to_crs('epsg:3857')['geometry'].unary_union.area/1e6, evacuation_zone_gdf.to_crs('epsg:3857').buffer(1609).unary_union.area/1e6))

    agents = demand(nodes_osmid_dict, dept_time_df=dept_time_df, demand_files = demand_files, phase_tdiff=phase_tdiff, reroute_pct=reroute_pct)
    agent_id_dict = {agent.id: agent for agent in agents}

    # ### fire growth
    # # fire_frontier = pd.read_csv(open(work_dir + '/projects/berkeley/demand_inputs/fire_fitted_ellipse.csv'))
    # # fire_frontier['t'] = (fire_frontier['t']-900)/fire_speed ### suppose fire starts at 11.15am
    # # fire_frontier = gpd.GeoDataFrame(fire_frontier, crs='epsg:4326', geometry=fire_frontier['geometry'].map(loads))
    link_fire_dist_dict = road_to_fire_dist(link_id_dict, fire_df)
    pd.DataFrame([[link_id, link_fire_dist, link_id_dict[link_id].geometry] for link_id, link_fire_dist in link_fire_dist_dict.items()], columns=['link_id', 'link_fire_dist', 'geometry']).to_csv(scratch_dir + simulation_outputs + '/fire/road_fire_dist_fs{}.csv'.format(fs), index=False)
    fire_df.to_csv(scratch_dir + simulation_outputs + '/fire/fire_init_fs{}.csv'.format(fs), index=False)
    
    t_s, t_e = 0, 7201
    traffic_counter = {21806:0, 11321:0}
    shelter_list = []
    ### time step output
    with open(scratch_dir + simulation_outputs + '/t_stats/t_stats_{}.csv'.format(scen_nm), 'w') as t_stats_outfile:
        t_stats_outfile.write(",".join(['t', 'arr', 'move', 'avg_fdist', 'neg_fdist', 'out_evac_zone_cnts', 'out_evac_buffer_cnts', 'into_21806', 'into_11321'])+"\n")

    for t in range(t_s, t_e):
        t_tstep_0 = time.time()
        move = 0

        ### initial routing
        if t==0: route(scen_nm=scen_nm, who='all')
        ### temporary
        for link in link_id_dict.values(): link.travel_time_list = []
        # ### if no rerouting, then just update the link traversal time
        # if reroute_pct == 0:
        #     for link_id, link in link_id_dict.items(): link.update_travel_time(t, link_time_lookback_freq=link_time_lookback_freq, g=g, update_graph=False)
        # ### if rerouting, at every reroute_freq
        # elif t%reroute_freq == 0:
        #     ### update link travel time
        #     for link_id, link in link_id_dict.items(): link.update_travel_time(t, link_time_lookback_freq=link_time_lookback_freq, g=g, update_graph=True)
        #     ### and rerouting a subset of agents
        #     route(scen_nm=scen_nm, who='gps')
        # ### rerouting but not at this time step
        # else: pass

        ### load agents
        new_shelter_list = []
        for agent_id, agent in agent_id_dict.items():
            agent.load_trips(t, node2link_dict=node2link_dict, link_id_dict=link_id_dict)
            ### reroute
            if (t>0) and (t%reroute_freq == 0):
                routing_status = agent.get_path()
                new_shelter_list.append(agent_id)
        for agent_id in new_shelter_list:
            del agent_id_dict[agent_id]

        
        ### link model
        ### Each iteration in the link model is not time-consuming. So just keep using one process.
        t_link_0 = time.time()
        # links_to_run = [link for link in link_id_dict.values() if (len(link.run_veh)>0) or (len(link.queue_veh)>0)]
        for link in link_id_dict.values(): link.run_link_model(t, agent_id_dict=agent_id_dict)
        
        ### node model
        t_node_0 = time.time()
        node_ids_to_run = set([link.end_nid for link in link_id_dict.values() if len(link.queue_veh)>0])
        for node_id in node_ids_to_run:
            node = node_id_dict[node_id] 
            n_t_move, t_traffic_counter, agent_update_dict, link_update_dict = node.run_node_model(t, node_id_dict=node_id_dict, link_id_dict=link_id_dict, agent_id_dict=agent_id_dict, node2link_dict=node2link_dict)
            move += n_t_move
            for agent_id, agent_new_info in agent_update_dict.items():
                [agent_id_dict[agent_id].cls, agent_id_dict[agent_id].cle, agent_id_dict[agent_id].status, agent_id_dict[agent_id].cl_enter_time] = agent_new_info
            for link_id, link_new_info in link_update_dict.items():
                if len(link_new_info) == 3:
                    [link_id_dict[link_id].queue_veh, link_id_dict[link_id].ou_c, link_id_dict[link_id].travel_time_list] = link_new_info
                elif len(link_new_info) == 2:
                    [link_id_dict[link_id].run_veh, link_id_dict[link_id].in_c] = link_new_info
                else:
                    print('invalid link update information')
        # for k, v in t_traffic_counter.items():
        #     try: traffic_counter[k] += v
        #     except KeyError: traffic_counter[k] = v
        t_node_1 = time.time()
        t_tstep_1 = time.time()
        # print(t, len(node_ids_to_run), t_node_1 - t_node_0, len(links_to_run), t_link_1 - t_link_0, t_tstep_1-t_tstep_0)

        ### metrics
        if t%100 == 0:
            arrival_cnts = np.sum([1 for a in agent_id_dict.values() if a.status=='arr'])
            if arrival_cnts == len(agent_id_dict):
                logging.info("all agents arrive at destinations")
                break
            veh_loc = [link_id_dict[node2link_dict[(agent.cls, agent.cle)]].midpoint for agent in agent_id_dict.values() if agent.status != 'arr']
            outside_evacuation_zone_cnts, outside_evacuation_buffer_cnts = outside_polygon(evacuation_zone, evacuation_buffer, veh_loc)
            avg_fire_dist = 0 # np.mean(fire_point_distance(veh_loc))
            neg_dist = cnt_veh_in_fire(veh_loc=veh_loc, fire_df=fire_df)
            with open(scratch_dir + simulation_outputs + '/t_stats/t_stats_{}.csv'.format(scen_nm),'a') as t_stats_outfile:
                t_stats_outfile.write(",".join([str(x) for x in [t, arrival_cnts, move, round(avg_fire_dist,2), neg_dist, outside_evacuation_zone_cnts, outside_evacuation_buffer_cnts, traffic_counter[21806], traffic_counter[11321]]]) + "\n")

            ### fitness metric
            fitness += neg_dist
        
        ## stepped outputs
        # if t%12000==0:
        #     link_output = pd.DataFrame([(link.id, len(link.queue_veh), len(link.run_veh), round(link.travel_time, 2)) for link in link_id_dict.values() if link.type=='real'], columns=['link_id', 'q', 'r', 't'])
        #     link_output[(link_output['q']>0) | (link_output['r']>0)].reset_index(drop=True).to_csv(scratch_dir + simulation_outputs + '/link_stats/link_stats_{}_t{}.csv'.format(scen_nm, t), index=False)
        #     node_predepart = pd.DataFrame([(agent.cle, 1) for agent in agent_id_dict.values() if (agent.status in [None, 'loaded'])], columns=['node_id', 'predepart_cnt']).groupby('node_id').agg({'predepart_cnt': np.sum}).reset_index()
        #     node_predepart.to_csv(scratch_dir + simulation_outputs + '/node_stats/node_stats_{}_t{}.csv'.format(scen_nm, t), index=False)

        if t%100==0: 
            logging.info(" ".join([str(i) for i in [t, arrival_cnts, move, round(avg_fire_dist,2), neg_dist, outside_evacuation_zone_cnts, outside_evacuation_buffer_cnts]]) + " " + str(len(veh_loc)))

    return fitness


### python3 -c 'import dta_meso_butte; dta_meso_butte.main(random_seed=0, dept_time_id="imm", reroute_pct=0, phase_tdiff=0, counterflow=0)'
if __name__ == "__main__":
    main(random_seed=0, dept_time_id=1, reroute_pct=0, phase_tdiff=0, counterflow=0)