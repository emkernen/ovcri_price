
# import os
# os.chdir(r"c:\Users\Tyler Price\Documents\Elena")

import json
import pandas as pd
from pandas import to_datetime
import numpy as np
from datetime import date, timedelta

# Open the JSON file
with open('trainings.txt', 'r') as f:
    # Load the JSON data into a Python dictionary
    data = json.load(f)

################################################################
# turn JSON data into Pandas data frame
name,tsp,exp = [],[],[]
for item in data:
     for data_item in item['completions']:
        name.append(data_item[u'name'])
        tsp.append(data_item[u'timestamp'])
        exp.append(data_item[u'expires'])
df = pd.DataFrame([name,tsp,exp]).T
# Group by training and count total completions (may include duplicate users)
grouped_df = df.groupby([0])[0].count().to_json()
# Save JSON to a file
with open('prompt1.json', 'w') as f:
    f.write(grouped_df)

#################################################################

# turn JSON data into Pandas data frame
user,name,tsp,exp = [],[],[],[]
for item in data:
     for data_item in item['completions']:
        user.append(item[u'name'])
        name.append(data_item[u'name'])
        tsp.append(data_item[u'timestamp'])
        exp.append(data_item[u'expires'])
df = pd.DataFrame([user,name,tsp,exp]).T

# Apply filters- filter to three specific trainings and filter by date
filtered_df = df[df[1].isin(['X-Ray Safety','Electrical Safety for Labs','Laboratory Safety Training'])]
filtered_df[2] = pd.to_datetime(filtered_df[2])
filtered_df2 = filtered_df.loc[filtered_df[2] >= '2023-07-01']
filtered_df3 = filtered_df2.loc[filtered_df2[2] <= '2024-06-30',[0,1]].rename(columns={0: 'user', 1: 'training'})

# Group by training, remove duplicates, and collect users into lists
training_dict = filtered_df3.groupby('training')['user'].apply(lambda x: list(set(x))).to_dict()

training_json = json.dumps(training_dict, indent=4)

# Save the JSON to a file
with open('prompt2.json', 'w') as f:
    f.write(training_json)

###############################################################

# turn JSON data into Pandas data frame
user,name,tsp,exp = [],[],[],[]
for item in data:
     for data_item in item['completions']:
        user.append(item[u'name'])
        name.append(data_item[u'name'])
        tsp.append(data_item[u'timestamp'])
        exp.append(data_item[u'expires'])
df = pd.DataFrame([user,name,tsp,exp]).T.rename(columns={0: 'user', 1: 'training', 2:'timestamp', 3:'expires'}).fillna('12/31/2100')
df['expires'] = to_datetime(df['expires'])
df['timestamp'] = (to_datetime(df['timestamp'])).dt.strftime("%Y-%m-%d")
# Identify training with latest expiration date 
df['C'] = df.sort_values(['expires'], ascending=True).groupby(['user', 'training']).cumcount() + 1

# Filter to trainings with most recent expiration dates, and then filter to those expired or nearly expired by the date
df = df[df['C'] == 1]
df = df.loc[df['expires'] <= to_datetime(date(2023, 10, 1) + timedelta(days=30))]
df['expiration_status'] = np.where(df['expires'] > '2023-10-01', "expires soon", "expired")
df['expires'] = (df['expires']).dt.strftime("%Y-%m-%d")

# Eliminate unnecessary columns
df = df[['user', 'training', 'timestamp', 'expires', 'expiration_status']]

# Save JSON to a file
final_df = df.to_json(orient = 'records')
with open('prompt3.json', 'w') as f:
    f.write(final_df) 
