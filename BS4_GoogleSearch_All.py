#!/usr/bin/env python
# coding: utf-8

# In[1]:


# importing necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from googletrans import Translator, constants
import numpy as np

# importing user-defined libraries
from lib import *


# In[2]:


# inputs
# entity = "Strukton"
n_pages = 4


# In[3]:


# building the search query
query = '(“Strukton”) AND scandal OR fraud OR investigation OR investigate OR litigation OR crime OR arrest OR allege OR guilty OR illegal OR indict OR terrorism OR terrorist OR smuggle OR smuggling OR corruption OR testify OR racketeer OR incriminate OR mafia OR convicted OR conviction OR accused OR defraud OR controversy OR controversial OR jail'


# In[4]:


# dummying the header to provide the functionality of a bot to the web-crawler
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

r = requests.get("https://www.google.com/search?q=" + query, headers = headers)


# In[5]:


# getting the text response and parsing HTML
c = r.text
soup = BeautifulSoup(c, "html.parser")


# In[6]:


# getting all the google searches and related data
search_data = soup.find_all("div", {"class" : "g"})


# In[7]:


# scraping all the search links appearing in the number of pages requested in the input

all_search_dict = {'URL': [], 'Date' : []}
for page_no in range(1, n_pages):
    n_searches = len(search_data)
    for search in range(n_searches):
        search_result = search_data[search]
        ## getting the search URL
        url = search_result.find("a").get("href")
        all_search_dict['URL'].append(url)

        try:
            ## trying to get the search date
            date_section = search_result.find('span', {"class":"MUxGbd wuQ4Ob WZ8Tjf"}).find_all('span')
            for element in date_section:
                text_element = element.text
                if date_checker(text_element):
                    date = text_element
                    break
        except:
            ## if no search date can be found...
            date = ""
            
        all_search_dict['Date'].append(date)
    
    ## navigating to the next page and scraping the subsequent google search URLs
    search_page = "Page " + str(page_no + 1)
    search_url = soup.find("a", {"aria-label" : search_page}).get("href")
    r = requests.get("https://www.google.com" + search_url, headers = headers)
    c = r.text
    soup = BeautifulSoup(c, "html.parser")
    search_data = soup.find_all("div", {"class" : "g"})


# In[8]:


# converting the dictionary containing URL and Timestamp for each link into a DataFrame
search_df = pd.DataFrame(all_search_dict)


# In[9]:


# getting the Source and Headline from the URL
search_df['Source'] = search_df['URL'].apply(extract_sourcename)
search_df['Heading'] = search_df['URL'].apply(extract_headline)


# In[10]:


# compiling the search dataframe
search_df.head()


# In[11]:


# reading the date and applying date processing
search_df['Date'] = search_df['Date'].apply(date_processor)
search_df.head()


# In[ ]:


search_df.to_excel('Google_Search_All.xlsx', index = False)

