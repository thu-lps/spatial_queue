import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

case = 'fairfax'

background_path_sn = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn/arrivals_{}_vect_bg_1_real_departure_time_total.csv'.format(case,case)
background_sn = pd.read_csv(background_path_sn)

background_path_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_total.csv'.format(case,case)
background_reroute = pd.read_csv(background_path_reroute)

background_path_sn_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_total.csv'.format(case,case)
background_sn_reroute = pd.read_csv(background_path_sn_reroute)

background_path_sn_rtt = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_rtt/arrivals_{}_vect_bg_1_real_departure_time_total.csv'.format(case,case)
background_sn_rtt = pd.read_csv(background_path_sn_rtt)

background_path_fft = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_ftt/arrivals_{}_vect_bg_1_real_departure_time_total.csv'.format(case,case)
background_fft = pd.read_csv(background_path_fft)

plt.figure(1)

plt.plot(background_sn['t'], background_sn['arrival_count'], color = 'r', label = 'total_traffic (Strategy1: check and destroy \n dead locks every 10 mins + fft)')
plt.plot(background_reroute['t'], background_reroute['arrival_count'], color = 'b', label = 'total_traffic (Strategy2: reroute every 31 mins + rtt)')
plt.plot(background_sn_reroute['t'], background_sn_reroute['arrival_count'], color = 'g', label = 'total_traffic (Strategy3: Strategy1 + Strategy2)')
plt.plot(background_sn_rtt['t'], background_sn_rtt['arrival_count'], color = 'k', label = 'total_traffic (Strategy4: Strategy1 + rtt)')
plt.plot(background_fft['t'][:600], background_fft['arrival_count'][:600], color = 'purple', ls = '--', label = 'total_traffic (Strategy5: fft)')



plt.xlabel('Simulation time')
plt.ylabel('Number of agents arriving at the destination')

plt.legend()
#plt.text(35000,60000, 'Strategy: destroy dead locks')
plt.tight_layout()

plt.savefig('./traffic_outputs/{}/{}_total_traffic.jpg'.format(case,case), dpi = 800)




plt.figure(2)
evacuation_path_sn = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn/arrivals_{}_vect_bg_1_real_departure_time_evacuation.csv'.format(case,case)
evacuation_sn = pd.read_csv(evacuation_path_sn)

evacuation_path_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_evacuation.csv'.format(case,case)
evacuation_reroute = pd.read_csv(evacuation_path_reroute)

evacuation_path_sn_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_reroute_rtt/arrivals_{}_vect_bg_1_real_departure_time_evacuation.csv'.format(case,case)
evacuation_sn_reroute = pd.read_csv(evacuation_path_sn_reroute)

evacuation_path_sn_rtt = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_add_srsn_rtt/arrivals_{}_vect_bg_1_real_departure_time_evacuation.csv'.format(case,case)
evacuation_sn_rtt = pd.read_csv(evacuation_path_sn_rtt)

evacuation_path_fft = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_ftt/arrivals_{}_vect_bg_1_real_departure_time_evacuation.csv'.format(case,case)
evacuation_fft = pd.read_csv(evacuation_path_fft)

plt.plot(evacuation_sn['t'], evacuation_sn['arrival_count'], color = 'r', label = 'evacuation_traffic (Strategy1: check and destroy \n dead locks every 10 mins + fft)')
plt.plot(evacuation_reroute['t'], evacuation_reroute['arrival_count'], color = 'b', label = 'evacuation_traffic (Strategy2: reroute every 31 mins + rtt)')
plt.plot(evacuation_sn_reroute['t'], evacuation_sn_reroute['arrival_count'], color = 'g', label = 'evacuation_traffic (Strategy3: Strategy1 + Strategy2)')
plt.plot(evacuation_sn_rtt['t'], evacuation_sn_rtt['arrival_count'], color = 'k', label = 'evacuation_traffic (Strategy4: Strategy1 + rtt)')
plt.plot(evacuation_fft['t'][:600], evacuation_fft['arrival_count'][:600], color = 'purple', ls = '--', label = 'evacuation_traffic (Strategy5: fft)')


plt.xlabel('Simulation time')
plt.ylabel('Number of agents arriving at the destination')
plt.legend()
plt.tight_layout()

plt.savefig('./traffic_outputs/{}/{}_evacuation_traffic.jpg'.format(case,case), dpi = 800)


plt.figure(3)
plt.plot(evacuation_sn['t'], background_sn['arrival_count'] - evacuation_sn['arrival_count'], color = 'r', label = 'background_traffic (Strategy1: check and destroy \n dead locks every 10 mins + fft)')
plt.plot(evacuation_reroute['t'], background_reroute['arrival_count'] - evacuation_reroute['arrival_count'], color = 'b', label = 'background_traffic (Strategy2: reroute every 31 mins + rtt)')
plt.plot(evacuation_sn_reroute['t'], background_sn_reroute['arrival_count'] - evacuation_sn_reroute['arrival_count'], color = 'g', label = 'background_traffic (Strategy3: Strategy1 + Strategy2)')
plt.plot(evacuation_sn_rtt['t'], background_sn_rtt['arrival_count'] - evacuation_sn_rtt['arrival_count'], color = 'k', label = 'background_traffic (Strategy4: Strategy1 + rtt)')
plt.plot(evacuation_fft['t'][:600], background_fft['arrival_count'][:600] - evacuation_fft['arrival_count'][:600], color = 'purple', ls = '--', label = 'background_traffic (Strategy5: fft)')


plt.xlabel('Simulation time')
plt.ylabel('Number of agents arriving at the destination')
plt.legend()
plt.tight_layout()

plt.savefig('./traffic_outputs/{}/{}_background_traffic.jpg'.format(case,case), dpi = 800)
plt.show()