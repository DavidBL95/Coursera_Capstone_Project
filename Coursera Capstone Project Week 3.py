#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np

import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

import json

get_ipython().system('conda install -c conda-forge geopy --yes')
from geopy.geocoders import Nominatim

import requests

get_ipython().system('conda install -c conda-forge beautifulsoup4 --yes')
from bs4 import BeautifulSoup

from pandas.io.json import json_normalize

import matplotlib.cm as cm
import matplotlib.colors as colors

from sklearn.cluster import KMeans

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium

print("Done")


# # IBM Applied Data Science Capstone Course by Coursera

# # Week 3 Project

# ### Part 1

# ###### Grab data from Wikipedia and put it into data frame

# In[2]:


data = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text


# In[3]:


soup = BeautifulSoup(data,'html.parser')


# In[4]:


postalCodeList= []
boroughList = []
neighborhoodList = []


# In[5]:


for row in soup.find('table').find_all('tr'):
    cells = row.find_all('td')
    if(len(cells) > 0):
        postalCodeList.append(cells[0].text)
        boroughList.append(cells[1].text)
        neighborhoodList.append(cells[2].text.rstrip('\n'))

postalCodeListFinal = []
boroughListFinal = []
neighborhoodListFinal = []
                              
for i in postalCodeList:
    postalCodeListFinal.append(i.rstrip('\n'))
    
for i in boroughList:
    boroughListFinal.append(i.rstrip('\n'))
    
for i in neighborhoodList:
    neighborhoodListFinal.append(i.rstrip('\n'))


# In[6]:


toronto_df = pd.DataFrame({"Postal Code": postalCodeListFinal,
                           "Borough": boroughListFinal,
                           "Neighborhood": neighborhoodListFinal})
toronto_df.head()


# ##### Drop cells with a borough that is "Not assigned"

# In[7]:


toronto_df_dropna = toronto_df[toronto_df.Borough != "Not assigned"].reset_index(drop=True)
toronto_df_dropna.head()


# ##### Group neighborhoods in the same borough

# In[8]:


toronto_df_grouped = toronto_df_dropna.groupby(["Postal Code", "Borough"], as_index=False).agg('min')
toronto_df_grouped.head()


# ##### For Neighborhood = "Not Assigned," make the value the same as Borough

# In[9]:


for index, row in toronto_df_grouped.iterrows():
    if row['Neighborhood'] == "Not Assigned":
        row['Neighborhood'] = row['Borough']
        
toronto_df_grouped.head()


# ##### Check whether it is the same

# In[10]:


column_names = ["Postal Code", "Borough", "Neighborhood"]
test_df = pd.DataFrame(columns=column_names)

test_list = ["M5G", "M2H", "M4B", "M1J", "M4G", "M4M", "M1R", "M9V", "M9L", "M5V", "M1B", "M5A"]

for postcode in test_list:
    test_df = test_df.append(toronto_df_grouped[toronto_df_grouped["Postal Code"]==postcode], ignore_index=True)
    
test_df


# In[11]:


toronto_df_grouped.shape


# ### Part 2

# ##### Load the coordinates from the csv file

# In[12]:


coordinates = pd.read_csv("Geospatial_Coordinates.csv")
coordinates.head()


# ##### Merge two tables to get the coordinates

# In[13]:


toronto_df_new = toronto_df_grouped.merge(coordinates, on="Postal Code", how = "left")
toronto_df_new.head()


# ##### Check coordinates were added

# In[14]:


column_names = ["Postal Code", "Borough", "Neighborhood", "Latitude", "Longitude"]
test_df = pd.DataFrame(columns=column_names)

test_list = ["M5G","M2H","M4B","M1J","M4G","M4M","M1R","M9V","M9L","M5V","M1B","M5A"]

for postcode in test_list:
    test_df = test_df.append(toronto_df_new[toronto_df_new["Postal Code"]==postcode], ignore_index=True)
    
test_df


# ### Part 3

# ##### Use Geopy library to get the coordinate values of Toronto

# In[15]:


address = 'Toronto'

geolocator = Nominatim(user_agent='my-application')
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The coordinates of Toronto are {}, {}.'.format(latitude,longitude))


# ##### Create map of Toronto with neighborhoods

# In[20]:


map_toronto = folium.Map(location=[latitude,longitude], zoom_start=11)

for lat, lng, borough, neighborhood in zip(toronto_df_new['Latitude'], toronto_df_new['Longitude'], toronto_df_new['Borough'], toronto_df_new['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat,lng],
        radius = 5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3256cc',
        fill_opacity=0.6).add_to(map_toronto)

map_toronto


# ##### Filter borough that contain the word Toronto

# In[21]:


borough_names = list(toronto_df_new.Borough.unique())

borough_with_toronto = []

for x in borough_names:
    if "toronto" in x.lower():
        borough_with_toronto.append(x)

borough_with_toronto


# In[22]:


toronto_df_new = toronto_df_new[toronto_df_new['Borough'].isin(borough_with_toronto)].reset_index(drop=True)

print(toronto_df_new.shape)
toronto_df_new.head()


# In[24]:


map_toronto = folium.Map(location=[latitude, longitude], zoom_start=11)

for lat, lng, borough, neighborhood in zip(toronto_df_new['Latitude'], toronto_df_new['Longitude'], toronto_df_new['Borough'], toronto_df_new['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3256cc',
        fill_opacity=0.6).add_to(map_toronto)  
    
map_toronto


# ##### Explore neighborhoods with Foursquare

# In[25]:


CLIENT_ID = '0N3DNNU34YQAFDV0XOUTDZ43QLI4FW34EDA3HFOCC5N0DJVX'
CLIENT_SECRET = 'J3CU3TVRT1TFETDEUVCPGLMUBG33GAPTKEMUQEG24UGXLQ50'
VERSION = '20180605'

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# ##### Get top 10 venues within a 500 meter radius

# In[27]:


radius = 500
LIMIT = 100

venues = []

for lat, long, post, borough, neighborhood in zip(toronto_df_new['Latitude'], toronto_df_new['Longitude'], toronto_df_new['Postal Code'], toronto_df_new['Borough'], toronto_df_new['Neighborhood']):
    url = "https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}".format(
        CLIENT_ID,
        CLIENT_SECRET,
        VERSION,
        lat,
        long,
        radius, 
        LIMIT)
    
    results = requests.get(url).json()["response"]['groups'][0]['items']
    
    for venue in results:
        venues.append((
            post, 
            borough,
            neighborhood,
            lat, 
            long, 
            venue['venue']['name'], 
            venue['venue']['location']['lat'], 
            venue['venue']['location']['lng'],  
            venue['venue']['categories'][0]['name']))


# In[28]:


venues_df = pd.DataFrame(venues)

venues_df.columns = ['Postal Code', 'Borough', 'Neighborhood', 'BoroughLatitude', 'BoroughLongitude', 'VenueName', 'VenueLatitude', 'VenueLongitude', 'VenueCategory']

print(venues_df.shape)
venues_df.head()


# In[30]:


venues_df.groupby(["Postal Code", "Borough", "Neighborhood"]).count()


# In[31]:


print('There are {} uniques categories.'.format(len(venues_df['VenueCategory'].unique())))


# In[32]:


venues_df['VenueCategory'].unique()[:50]


# In[33]:


toronto_onehot = pd.get_dummies(venues_df[['VenueCategory']], prefix="", prefix_sep="")

toronto_onehot['Postal Code'] = venues_df['Postal Code'] 
toronto_onehot['Borough'] = venues_df['Borough'] 
toronto_onehot['Neighborhoods'] = venues_df['Neighborhood'] 

fixed_columns = list(toronto_onehot.columns[-3:]) + list(toronto_onehot.columns[:-3])
toronto_onehot = toronto_onehot[fixed_columns]

print(toronto_onehot.shape)
toronto_onehot.head()


# In[42]:


toronto_grouped = toronto_onehot.groupby(["Postal Code", "Borough", "Neighborhoods"]).mean().reset_index()

print(toronto_grouped.shape)


# In[43]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

areaColumns = ['Postal Code', 'Borough', 'Neighborhoods']
freqColumns = []
for ind in np.arange(num_top_venues):
    try:
        freqColumns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        freqColumns.append('{}th Most Common Venue'.format(ind+1))
columns = areaColumns+freqColumns

neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Postal Code'] = toronto_grouped['Postal Code']
neighborhoods_venues_sorted['Borough'] = toronto_grouped['Borough']
neighborhoods_venues_sorted['Neighborhoods'] = toronto_grouped['Neighborhoods']

for ind in np.arange(toronto_grouped.shape[0]):
    row_categories = toronto_grouped.iloc[ind, :].iloc[3:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    neighborhoods_venues_sorted.iloc[ind, 3:] = row_categories_sorted.index.values[0:num_top_venues]

print(neighborhoods_venues_sorted.shape)


# ##### Clustering

# In[44]:


kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop(["Postal Code", "Borough", "Neighborhoods"], 1)

kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

kmeans.labels_[0:10]


# In[45]:


toronto_merged = toronto_df_new.copy()

toronto_merged["Cluster Labels"] = kmeans.labels_

toronto_merged = toronto_merged.join(neighborhoods_venues_sorted.drop(["Borough", "Neighborhoods"], 1).set_index("Postal Code"), on="Postal Code")

print(toronto_merged.shape)
toronto_merged.head()


# In[46]:


print(toronto_merged.shape)
toronto_merged.sort_values(["Cluster Labels"], inplace=True)


# In[48]:


map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

x = np.arange(kclusters)
ys = [i+x+(i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

markers_colors = []
for lat, lon, post, bor, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'], toronto_merged['Postal Code'], toronto_merged['Borough'], toronto_merged['Neighborhood'], toronto_merged['Cluster Labels']):
    label = folium.Popup('{} ({}): {} - Cluster {}'.format(bor, post, poi, cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.6).add_to(map_clusters)
       
map_clusters


# In[ ]:




