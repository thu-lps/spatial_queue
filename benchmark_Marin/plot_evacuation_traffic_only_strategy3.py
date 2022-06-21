import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

############################################################## PART 1 ##############################################################
### 分开画total traffic, evacuation traffic, background traffic 三者的图
'''
case = 'fairfax'


background_path_sn_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_total.csv'.format(case,case)
background_sn_reroute = pd.read_csv(background_path_sn_reroute)


plt.figure(1)


plt.plot(background_sn_reroute['t'], background_sn_reroute['arrival_count'], color = 'g', label = 'total traffic')



plt.xlabel('Time [h]')
plt.ylabel('Number of agents arriving at the destination')
plt.xticks(np.arange(0,21601, 3600), np.arange(6,13,1))

plt.legend()
#plt.text(35000,60000, 'Strategy: destroy dead locks')
plt.tight_layout()

plt.savefig('./traffic_outputs/{}/{}_total_traffic_strategy3.jpg'.format(case,case), dpi = 800)




plt.figure(2)

evacuation_path_sn_reroute = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_evacuation.csv'.format(case,case)
evacuation_sn_reroute = pd.read_csv(evacuation_path_sn_reroute)

plt.plot(evacuation_sn_reroute['t'], evacuation_sn_reroute['arrival_count'], color = 'r', label = 'evacuation traffic')


plt.xlabel('Time [h]')
plt.ylabel('Number of agents arriving at the destination')
plt.xticks(np.arange(0,21601, 3600), np.arange(6,13,1))
plt.legend()
plt.tight_layout()

plt.savefig('./traffic_outputs/{}/{}_evacuation_traffic_strategy3.jpg'.format(case,case), dpi = 800)


plt.figure(3)

plt.plot(evacuation_sn_reroute['t'], background_sn_reroute['arrival_count'] - evacuation_sn_reroute['arrival_count'], color = 'b', label = 'background traffic')


plt.xlabel('Time [h]')
plt.ylabel('Number of agents arriving at the destination')
plt.xticks(np.arange(0,21601, 3600), np.arange(6,13,1))
plt.legend()
plt.tight_layout()

plt.savefig('./traffic_outputs/{}/{}_background_traffic_strategy3.jpg'.format(case,case), dpi = 800)
plt.show()
'''

'''
############################################################## PART 2 ##############################################################
### evacuation 和 background traffic 放在一起
case = 'fairfax'


background_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_total.csv'.format(case,case)
background = pd.read_csv(background_path)

evacuation_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_evacuation.csv'.format(case,case)
evacuation = pd.read_csv(evacuation_path)

background['arrival_count'] = background['arrival_count'] - evacuation['arrival_count']

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

ax1.plot(evacuation['t'], evacuation['arrival_count'], color = 'r', label = 'evacuation traffic')
ax1.set_xlabel('Time [h]')
ax1.set_ylabel('Number of evacuees who reach the destination')
ax1.set_ylim([0,4400]) #fairfax 4400

ax1.set_xticks(np.arange(0,25201, 3600))
ax1.set_xticklabels(np.arange(6,14,1))
plt.legend()

axins = inset_axes(ax1, width=3, height=1.5, loc='lower right')
axins.plot(background['t'], background['arrival_count'], color = 'b', label = 'background traffic')
axins.set_xticks(np.arange(0,25201, 3600))
axins.set_xticklabels(np.arange(6,14,1))
axins.xaxis.set_ticks_position('top')
axins.legend()

plt.savefig('./traffic_outputs/{}/{}_results.jpg'.format(case,case), dpi = 800)
plt.show()
'''


############################################################## PART 3 ##############################################################
### 不同时间段出发的evacuation 图放在一起比较
case = 'fairfax'

total_depart_6_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_total.csv'.format(case,case)
total_depart_7_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_total_depart_7.csv'.format(case,case)
total_depart_8_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_total_depart_8.csv'.format(case,case)
total_depart_9_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_total_depart_9.csv'.format(case,case)

total_depart_6 = pd.read_csv(total_depart_6_path)
total_depart_7 = pd.read_csv(total_depart_7_path)
total_depart_8 = pd.read_csv(total_depart_8_path)
total_depart_9 = pd.read_csv(total_depart_9_path)

evacuation_depart_6_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_evacuation.csv'.format(case,case)
evacuation_depart_7_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_evacuation_depart_7.csv'.format(case,case)
evacuation_depart_8_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_evacuation_depart_8.csv'.format(case,case)
evacuation_depart_9_path = '/Users/apple/Documents/GitHub/spatial_queue/benchmark_Marin/traffic_outputs/{}/with_bg/t_stats_final/arrivals_{}_vect_bg_1_evacuation_depart_9.csv'.format(case,case)

evacuation_depart_6 = pd.read_csv(evacuation_depart_6_path)
evacuation_depart_7 = pd.read_csv(evacuation_depart_7_path)
evacuation_depart_8 = pd.read_csv(evacuation_depart_8_path)
evacuation_depart_9 = pd.read_csv(evacuation_depart_9_path)

background_depart_6 = total_depart_6['arrival_count'] - evacuation_depart_6['arrival_count']
background_depart_7 = total_depart_7['arrival_count'] - evacuation_depart_7['arrival_count']
background_depart_8 = total_depart_8['arrival_count'] - evacuation_depart_8['arrival_count']
background_depart_9 = total_depart_9['arrival_count'] - evacuation_depart_9['arrival_count']

plt.figure(1)
plt.plot(evacuation_depart_6['t'], evacuation_depart_6['arrival_count'], color = 'r', label = 'departure time: 6 a.m.')
plt.plot(evacuation_depart_7['t'], evacuation_depart_7['arrival_count'], color = 'y', label = 'departure time: 7 a.m.')
plt.plot(evacuation_depart_8['t'], evacuation_depart_8['arrival_count'], color = 'b', label = 'departure time: 8 a.m.')
plt.plot(evacuation_depart_9['t'], evacuation_depart_9['arrival_count'], color = 'g', label = 'departure time: 9 a.m.')

plt.xlabel('Time [h]')
plt.ylabel('Number of agents which reach the destination')
plt.xticks(np.arange(0,21601, 3600), np.arange(6,13,1))
plt.legend()
plt.tight_layout()
plt.savefig('./traffic_outputs/{}/{}_evacuation_comparison_real_departure_time.jpg'.format(case, case), dpi = 800)

plt.figure(2)
plt.plot(evacuation_depart_6['t'][:108], evacuation_depart_6['arrival_count'][:108], color = 'r', label = 'departure time: 6 a.m.')
plt.plot(evacuation_depart_7['t'][36:180]-3600, evacuation_depart_7['arrival_count'][36:180], color = 'y', label = 'departure time: 7 a.m.')
plt.plot(evacuation_depart_8['t'][72:216]-7200, evacuation_depart_8['arrival_count'][72:216], color = 'b', label = 'departure time: 8 a.m.')
plt.plot(evacuation_depart_9['t'][108:252]-10800, evacuation_depart_9['arrival_count'][108:252], color = 'g', label = 'departure time: 9 a.m.')

plt.xlabel('Travel time [min]')
plt.ylabel('Number of agents which reach the destination')
plt.xticks(np.arange(0,18000, 1800), (np.arange(0,18000, 1800)/60).astype('int'))
plt.legend()
plt.tight_layout()
plt.savefig('./traffic_outputs/{}/{}_evacuation_comparison_relative_departure_time.jpg'.format(case, case), dpi = 800)



