import numpy as np
import pandas as pd
import random 
import math
import multiprocessing
import time
import os

link_data = pd.read_csv('new_fairfax_links.csv')
test_data = pd.read_csv('/Users/apple/Downloads/lfairfax_vect_at_26800_bg_1.csv')
link_data = link_data[['link_id', 'lanes']]

test_data = pd.merge(test_data,link_data, how = 'left', left_on = 'link_id', right_on = 'link_id')
test_data['queue_length_lanes'] = test_data['queue'] / test_data['length'] / test_data['lanes']
test_data.to_csv('/Users/apple/Downloads/lfairfax_vect_at_26800_bg_1_edited.csv')
