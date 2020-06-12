import scipy.io as sio
import json
import sys
import numpy as np 
import pandas as pd 
import geopandas as gpd
import os 
import random
import matplotlib as mpl 
import matplotlib.pyplot as plt 
import matplotlib.colors as pltcolors
import descartes 
import shapely
import shapely.wkt 
import shapely.ops
from shapely.geometry.point import Point
import gc 

absolute_path = '/home/bingyu/spatial_queue'

simulation_outputs = absolute_path + '/projects/bolinas_stinson_beach/simulation_outputs'
network_file_edges_expanded = simulation_outputs+'/links_expanded.csv'
visualization_outputs = absolute_path + '/projects/bolinas_stinson_beach/visualization_outputs'

def snapshot(t, game_veh_id, current_link_id, link_detailed_dict, road_gdf):

    ### road info
    current_link = road_gdf.loc[road_gdf['link_id']==current_link_id]
    connecting_nodes = [current_link['end_nid'].iloc[0]]
    connecting_links = road_gdf.loc[road_gdf['start_nid'].isin(connecting_nodes) | road_gdf['end_nid'].isin(connecting_nodes)]
    surrounding_area = current_link['geometry'].iloc[0].interpolate(0.5, normalized = True).buffer(300)
    surrounding_links = road_gdf[road_gdf['geometry'].within(surrounding_area)]
    sub_road_gdf = pd.concat([current_link, connecting_links, surrounding_links]).drop_duplicates().reset_index(drop=True)
    # sub_road_gdf = pd.concat([current_link, connecting_links]).drop_duplicates().reset_index(drop=True)

    ### veh info
    veh_list = []
    for link in sub_road_gdf.itertuples():
        link_id = getattr(link, 'link_id')
        link_geom = getattr(link, 'geometry')

        ### waiting
        if link_id[0] == 'n':
            for (w_veh_id, cl_enter_time) in link_detailed_dict[link_id]['queue']+link_detailed_dict[link_id]['run']:
                w_veh_coord = link_geom.interpolate(0.9, normalized=True)
                veh_list.append([w_veh_id, 'w', w_veh_coord.x, w_veh_coord.y])
            continue

        ### queuing
        link_fft = getattr(link, 'fft')
        link_length = link_geom.length
        queue_end = link_length - 4
        for (q_veh_id, cl_enter_time) in link_detailed_dict[link_id]['queue']:
            q_veh_loc = queue_end
            queue_end = max(queue_end-8, 4)
            q_veh_coord = link_geom.interpolate(q_veh_loc/link_length, normalized=True)
            veh_list.append([q_veh_id, 'q', q_veh_coord.x, q_veh_coord.y])

        ### running
        for (r_veh_id, cl_enter_time) in link_detailed_dict[link_id]['run']:
            if link_length*(t-cl_enter_time)/link_fft>queue_end:
                r_veh_loc = queue_end
                queue_end = max(queue_end-8, 0)
            else:
                r_veh_loc = link_length*(t-cl_enter_time)/link_fft
            r_veh_loc = max(r_veh_loc, 4)
            r_veh_coord = link_geom.interpolate(r_veh_loc/link_length, normalized=True)
            veh_list.append([r_veh_id, 'r', r_veh_coord.x, r_veh_coord.y])
    veh_df = pd.DataFrame(veh_list, columns=['veh_id', 'status', 'lon', 'lat'])
    veh_gdf = gpd.GeoDataFrame(veh_df, crs='epsg:26910', geometry=gpd.points_from_xy(veh_df.lon, veh_df.lat))
    veh_gdf.loc[veh_gdf['veh_id']==game_veh_id, 'status'] = 'g'

    def hex_color(c, ty):
        if (c=='n') and (ty=='road'):
            return '#%02X%02X%02X' % (200,200,200)
        elif (c!='n') and (ty=='road'):
            return '#%02X%02X%02X' % (0,0,0)
        # elif (c=='w') and (ty=='veh'):
        #     return '#%02X%02X%02X' % (256,0,0)
        # elif (c!='q') and (ty=='veh'):
        #     return '#%02X%02X%02X' % (0,256,0)
        # elif (c!='r') and (ty=='veh'):
        #     return '#%02X%02X%02X' % (0,256,0)
        # elif (c!='g') and (ty=='veh'):
        #     return '#%02X%02X%02X' % (256,0,256)
        elif (c=='w') and (ty=='veh'):
            return 'orange'
        elif (c=='q') and (ty=='veh'):
            return 'red'
        elif (c=='r') and (ty=='veh'):
            return 'green'
        elif (c=='g') and (ty=='veh'):
            return 'purple'
        else:
            return '#%02X%02X%02X' % (0,0,0)
    
    fig = plt.figure(figsize=(10, 10))
    ax1 = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    ax1.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)

    sub_road_gdf['color'] = sub_road_gdf['link_id'].apply(lambda x: hex_color(x[0], 'road'))
    sub_road_plot = sub_road_gdf.plot(ax=ax1, color=sub_road_gdf['color'])
    veh_gdf['color'] = veh_gdf['status'].apply(lambda x: hex_color(x, 'veh'))
    veh_plot = veh_gdf.plot(ax=ax1, marker='o', markersize=50, c=veh_gdf['color'])
    veh_plot = veh_gdf.loc[veh_gdf['veh_id']==game_veh_id].plot(ax=ax1, marker='o', markersize=500, c='purple')

    fig.text(0.5, 0.85, '{} sec into evacuation'.format(t), fontsize=30, ha='center', va='center')
    plt.savefig(visualization_outputs + '/veh_loc_plot/veh_loc_t{}.png'.format(t))#, transparent=True)
    plt.close()

def main():
    game_veh_id = 144
    scen_nm = 'game'
    road_df = pd.read_csv(network_file_edges_expanded)
    road_df['end_nid'] = road_df['end_nid'].astype(str)
    road_gdf = gpd.GeoDataFrame(road_df, crs='epsg:4326', geometry=road_df['geometry'].map(shapely.wkt.loads))
    road_gdf = road_gdf.to_crs("EPSG:26910")

    for t in range(0, 600, 10):
        current_link_id = None
        link_detailed_dict = json.load(open(simulation_outputs+'/link_detailed_outputs/link_detail_{}_t{}.json'.format(scen_nm, t)))
        
        for link_id, link_vehs in link_detailed_dict.items():
            if (game_veh_id in [queue_veh[0] for queue_veh in link_vehs['queue']]) or (game_veh_id in [run_veh[0] for run_veh in link_vehs['run']]):
                current_link_id = link_id
                # print(t, current_link_id)
                break
        
        if current_link_id is not None:
            snapshot(t, game_veh_id, current_link_id, link_detailed_dict, road_gdf)

def make_gif():
    import imageio
    images = []
    durations = []
    for t in range(0,600,10):
#         memory = make_img(t=t, memory=memory)
        images.append(imageio.imread(visualization_outputs + '/veh_loc_plot/veh_loc_t{}.png'.format(t)))
        if t%60 == 0:
            durations.append(8)
        else:
            durations.append(0.5)
    imageio.mimsave(visualization_outputs + '/veh_loc_plot/veh_loc_animation_fast.gif', images, duration=durations)

if __name__ == '__main__':
    # main()
    make_gif()