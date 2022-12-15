#!/usr/bin/env python
# coding: utf-8

# # Selecting the Top hits by year_quarter and adversity score 

# In[1]:


import pandas as pd
import math


# In[2]:


data = pd.read_excel('AMS (3).xlsx')


# In[3]:


#Picking the news that are related for the last five years
data1 = data.loc[data['Recency'] == 1]

# groupby the date by quarters
data2 = (data1
         .sort_values(by=['Date','Adversity Score'])
         .groupby(pd.Grouper(key='Date', freq="QS"))
         .apply(lambda x: x)
         .sort_values(by=['Date','Adversity Score'], ascending = [False, False]))

data2[ 'year_quarter' ] = data2.Date.dt.to_period('Q')
data2.head(5)


# In[4]:


# finding the proper sampling proportion of every quarter
proportion = 50 / len( data2 )
 
quarters_sampling_size_df = data2.groupby( "year_quarter" ).apply( lambda x: math.ceil(len(x) * proportion) )
quarters_sampling_size_df


# In[5]:


#Performing the sampling and sorting the reults descending based on the year-quarter column
final_hits = (
    data2
     .groupby( "year_quarter", as_index=False )
     .apply( lambda x: x.head( quarters_sampling_size_df[ x.year_quarter.iloc[0] ] ) )
     .sort_values( by="year_quarter", ascending=False )
     .set_index( "year_quarter" )
)

final_hits.to_csv( 'final_hits.csv' )
final_hits


# In[6]:


final_hits.shape


# In[ ]:




