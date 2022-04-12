import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import geopandas as gpd 
from shapely.wkt import loads 
from shapely.ops import substring


case = 'fairfax'
basemap = pd.read_csv('../traffic_inputs/fairfax/new_fairfax_links_tmp.csv')
basemap = gpd.GeoDataFrame(basemap, crs='epsg:4326', geometry=basemap['geometry'].map(loads)).to_crs(3857)
storage_dict = {getattr(link,'link_id') : getattr(link,'length') * getattr(link,'lanes') for link in basemap.itertuples()}

for t in range(10000, 10500, 500):#28900
    try:
        edges_df = pd.read_csv('./{}/with_bg/link_stats_add_srsn_reroute_rtt/l{}_vect_at_{}_bg_1_real_departure_time.csv'.format(case,case,t))
        edges_df = edges_df[~edges_df['geometry'].isnull()]
        edges_df['link_id'] = edges_df['link_id'].astype('int')
        edges_df['storage'] = edges_df['link_id'].map(storage_dict)
        edges_df['storage'] = np.where(edges_df['storage']<18, 18, edges_df['storage'])
        edges_df['density'] = (edges_df['run'] + edges_df['queue'])*8 / edges_df['storage']
        edges_gdf = gpd.GeoDataFrame(edges_df, crs='epsg:3857', geometry=edges_df['geometry'].map(loads))
    except FileNotFoundError:
        continue

    fig, ax = plt.subplots(figsize=(10, 10))
    basemap.plot(ax=ax, lw=0.2, color='gray')
    edges_gdf.plot(column = 'density', ax = ax, lw =1, cmap='OrRd', legend = False)
    ax.set_xlim([-13650000,-13621802]) #fairfax
    ax.set_ylim([4570000,4583611]) #fairfax
    #ax.axis('off')
    ax.text(0, 0.1, 't{}'.format(t), fontsize = 18, transform=ax.transAxes)
    #plt.savefig('images/{}/link_density/density_t{}.png'.format(case,t),dpi= 200)
    plt.show()