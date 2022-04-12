#!/usr/bin/env python
# coding: utf-8
import os, sys
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
from shapely.geometry import Point, LineString

### usr
abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, abs_path)
sys.path.insert(0, "/Users/apple/Documents/GitHub")
from sp import interface

#把bg的终点换成虚拟点，增加node,增加link
ods_df = pd.read_csv('fairfax_ods_background.csv',float_precision="round_trip")
nodes = pd.read_csv('fairfax_nodes.csv',float_precision="round_trip")
links_df = pd.read_csv('fairfax_links.csv',float_precision="round_trip")


def prepare_links(links_df):
    links_df['link_id'] = links_df['eid']
    links_df['start_node_id'] = links_df['nid_s']
    links_df['end_node_id'] = links_df['nid_e']
    ### links must contain the following columns; geometry must be in epsg:4326
    links = links_df[['link_id', 'start_node_id', 'end_node_id', 'geometry']].copy()
    links['link_type'] = 'real' #认为目前所有的link都是real
    
    ### add attributes
    links = gpd.GeoDataFrame(links, crs='epsg:4326', geometry=links_df['geometry'].map(loads)).to_crs('epsg:3857') #从4326转变成3857
    try: links['length'] = links_df['length'] #有长度增加长度属性
    except KeyError:
        links['length'] = links['geometry'].length #没有长度从geometry得到
        print('link length not specified; derive from geometry instead.')
    try: links['maxmph'] = links_df['maxmph'] #有速度增加速度属性
    except KeyError:
        links['maxmph'] = 25 #没有速度默认为25迈
        print('link speed limit (mph); use 25mph.')
    try: links['lanes'] = links_df['lanes'] #设置link的车道数
    except KeyError:
        links['lanes'] = 1 #没有车道默认为1
        print('link length not specified; assume one lane.')

    links['fft'] = links['length']/(links['maxmph']*1609/3600)
    links['capacity'] = links['lanes'] * 1000/3600
    links['storage'] = links['length'] * links['lanes']
    links['storage'] = np.where(links['storage']<18, 18, links['storage'])
    links = links[['link_id', 'start_node_id', 'end_node_id', 'link_type', 'length', 'lanes', 'maxmph', 'fft', 'capacity', 'storage', 'geometry']]

    return links

links = prepare_links(links_df)

g = interface.from_dataframe(self.links[self.links['link_type']=='real'], 'start_node_id', 'end_node_id', 'fft') #读取路网到g里

sp = g.dijkstra(ods_df['origin_node_id'][0], ods_df['destin_node_id'][0])
