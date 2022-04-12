import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

case = 'fairfax'


background_path_sn_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_total.csv'.format(case,case)
background_sn_reroute = pd.read_csv(background_path_sn_reroute)


background_path_sn_reroute_2 = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_total_random2.csv'.format(case,case)
background_sn_reroute_2 = pd.read_csv(background_path_sn_reroute_2)

plt.figure(1)

plt.plot(background_sn_reroute['t'], background_sn_reroute['arrival_count'], color = 'g', label = 'total_traffic (random seed = 1)')
plt.plot(background_sn_reroute_2['t'], background_sn_reroute_2['arrival_count'], color = 'r', label = 'total_traffic (random seed = 2)')



plt.xlabel('Simulation time')
plt.ylabel('Number of agents arriving at the destination')

plt.legend()
#plt.text(35000,60000, 'Strategy: destroy dead locks')
plt.tight_layout()

plt.savefig('./{}_total_traffic.jpg'.format(case,case), dpi = 800)




plt.figure(2)

evacuation_path_sn_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_evacuation.csv'.format(case,case)
evacuation_sn_reroute = pd.read_csv(evacuation_path_sn_reroute)

evacuation_path_sn_reroute_2 = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_evacuation_random2.csv'.format(case,case)
evacuation_sn_reroute_2 = pd.read_csv(evacuation_path_sn_reroute_2)


plt.plot(evacuation_sn_reroute['t'], evacuation_sn_reroute['arrival_count'], color = 'g', label = 'evacuation_traffic (Strategy3: random seed = 1)')
plt.plot(evacuation_sn_reroute_2['t'], evacuation_sn_reroute_2['arrival_count'], color = 'r', label = 'evacuation_traffic (Strategy3: random seed = 2)')


plt.xlabel('Simulation time')
plt.ylabel('Number of agents arriving at the destination')
plt.legend()
plt.tight_layout()

plt.savefig('./{}_evacuation_traffic.jpg'.format(case,case), dpi = 800)


plt.figure(3)

plt.plot(evacuation_sn_reroute['t'], background_sn_reroute['arrival_count'] - evacuation_sn_reroute['arrival_count'], color = 'g', label = 'background_traffic (random seed = 1)')
plt.plot(evacuation_sn_reroute_2['t'], background_sn_reroute_2['arrival_count'] - evacuation_sn_reroute_2['arrival_count'], color = 'r', label = 'background_traffic (random seed = 2)')


plt.xlabel('Simulation time')
plt.ylabel('Number of agents arriving at the destination')
plt.legend()
plt.tight_layout()

plt.savefig('./{}_background_traffic.jpg'.format(case,case), dpi = 800)
plt.show()