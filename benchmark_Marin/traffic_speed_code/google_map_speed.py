#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
import requests
import datetime, time
import matplotlib.pyplot as plt


# In[3]:


Route_dict = {}
# need to manually seach the route's origin and destiantion coordinates, as there is a little difference in the poistion of each coordinate reflected in the map between Google Map and OpenStreet Map
Route_dict['Route1'] = {'origin':(37.9953566, -122.596054), 'destination':(37.9874255,-122.5894828)} 
Route_dict['Route2'] = {'origin':(37.9874255,-122.5894828), 'destination':(37.9871674,-122.587166)}
Route_dict['Route3'] = {'origin':(37.982580,-122.592750), 'destination':(37.987055,-122.5888845)}
Route_dict['Route4'] = {'origin':(37.987055,-122.5888845), 'destination':(37.986885,-122.5871983)}
Route_dict['Route5'] = {'origin':(37.9871674,-122.587166), 'destination':(37.9868523,-122.5780141)}
Route_dict['Route6'] = {'origin':(37.9868523,-122.5780141), 'destination':(37.9765030,-122.561715)}
Route_dict['Route7'] = {'origin':(37.9763279,-122.5608459), 'destination':(37.9740093,-122.5414434)}
Route_dict['Route8'] = {'origin':(37.9737508,-122.5404851), 'destination':(37.9705599,-122.5223654)}
Route_dict['Route9'] = {'origin':(37.9705599,-122.5223654), 'destination':(37.9448588,-122.4843088)}


# In[4]:


API_KEY = 'xxx' # your API KEY


# In[5]:


weekday_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


# In[ ]:


speed_route_df = pd.DataFrame(columns = ['RouteID','length','week','hour','minute','travel_time','average_speed'])
while True:
    now = datetime.datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    current_second = now.second
    current_weekday = now.weekday() # week attribute
    current_month = now.month
    current_day = now.day
    #if current_hour in [1,2,3,4,5]:
    #    time.sleep(30)
    #    continue;
    if current_minute%10 == 0: # grab the screen every 10 minutes
        if current_minute == 0: #output the file every 1 hour
            if current_hour == 0:
                if current_weekday == 0:
                    speed_route_df.to_csv('./speed_average_Routes_python/{}_{}_speed.csv'.format(weekday_name[6], 23))
                else:
                    speed_route_df.to_csv('./speed_average_Routes_python/{}_{}_speed.csv'.format(weekday_name[current_weekday-1], 23))
            else:
                speed_route_df.to_csv('./speed_average_Routes_python/{}_{}_speed.csv'.format(weekday_name[current_weekday], current_hour-1))
            speed_route_df = pd.DataFrame(columns = ['RouteID','length','week','hour','minute','travel_time','average_speed'])
        
        print("now time is: ", now)
        absolute_seconds = int(time.mktime(datetime.datetime(2022,current_month,current_day,current_hour,current_minute,0).timetuple()))
        for route_id in Route_dict.keys():
            origin_coord = Route_dict.get(route_id).get('origin')
            destin_coord = Route_dict.get(route_id).get('destination')
            url = 'https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&departure_time={}&key={}'.format(
                    origin_coord[0], origin_coord[1], destin_coord[0], destin_coord[1], absolute_seconds, API_KEY)
            payload={}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            data=response.json()
            if 'routes' not in data.keys():
                print('1')
                continue
                if 'legs' not in data['routes'][0].keys():
                    print('2')
                    continue
                    if 'duration_in_traffic' not in data['routes'][0].get('legs')[0].keys():
                        print('3')
                        continue
            if current_hour == 18:
                print(data)
            route_length = data['routes'][0].get('legs')[0].get('distance').get('value')
            travel_time = data['routes'][0].get('legs')[0].get('duration_in_traffic').get('value')
            average_speed = route_length/travel_time
            time.sleep(1)
            print(route_id,average_speed)
            speed_route_df = speed_route_df.append([{'RouteID':route_id, 'length':route_length, 'week':weekday_name[current_weekday], 'hour':current_hour, 'minute':current_minute,
                                                'travel_time':travel_time, 'average_speed':average_speed}], ignore_index = True)
        time.sleep(540) # let the code sleep for 9 minutes
        


# In[ ]:




