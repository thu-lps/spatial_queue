import numpy as np
import pandas as pd
import random 
import math
import multiprocessing
import time
import os
import matplotlib.pyplot as plt

path = './fairfax/t_stats/arrivals_fairfax_vect_bg_1.csv'
data = pd.read_csv(path)
plt.figure()

plt.plot(data['t'], data['arrival_count'], color='r', label = 'fairfax_with_bg (simultaneously depart)')
plt.text(4000,1000, 'Wait for background traffic to evacuate first')
plt.legend()
plt.tight_layout()
plt.savefig('./fairfax_with_bg_real_time.jpg', dpi = 800)
