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


### spatial queue model
sys.path.insert(0, '..')



### Read network and demand
case='fairfax'


background_od = pd.read_csv('{}/background_ods_day_for_Marin_new_change_marin_side_od.csv'.format(case,case), float_precision = "round_trip")
background_od['departure_time'] = (background_od['departure_hour'] - 6) * 3600 + background_od['departure_quarter'] * 900
for i in range(len(background_od)):
    random.seed(i)
    background_od.loc[i,'departure_time'] = random.randint(background_od.loc[i, 'departure_time'], background_od.loc[i, 'departure_time'] + 900)



background_od.to_csv('./background_ods_day_for_Marin_new_change_marin_side_od.csv', index = False)


