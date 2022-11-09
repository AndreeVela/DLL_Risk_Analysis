import numpy as np
import re
import requests
import pandas as pd

from bs4 import BeautifulSoup
from googletrans import Translator, constants


# extracting the source of each of the URLs
def extract_sourcename(url):
    source_name = url.split('//')[1].split('/')[0]
    return source_name
    ## iff the source is a part of the entity's home (company) website, the URL is NOT CONSIDERED FOR AMS
    #if 'strukton' in source_name:
    #    return False
    #else:
    #    return source_name
    
    
# extracting the headline of each of the URLs
def extract_headline(url):
    i = 1
    while(1):
        if url.split('/')[-i] != '':
            headline = url.split('/')[-i]
            break
        else:
            i += 1
            
    headline = ' '.join(headline.split('-'))
    headline = headline[0].upper() + headline[1:]
    headline = re.sub('[^A-Za-z ]+', '', headline)
    
    # translating the headlines to English
    translator = Translator()
    headline_english = translator.translate(headline, dest='en').text
    return headline_english


def date_checker(text):
    # checking whether a 4-digit year
    if text.split()[-1].isnumeric() and int(text.split()[-1]) >= 1000:
        return True
    elif 'ago' in text:
        return True
    else:
        return False

def date_processor(date):
    month_to_num = {'jan.':'01',
                    'feb.':'02',
                    'mar.':'03',
                    'mrt.':'03',
                    'apr.':'04',
                    'may.':'05',
                    'mei' :'05',
                    'jun.':'06',
                    'juni':'06',
                    'jul.':'07',
                    'juli':'07',
                    'aug.':'08',
                    'sep.':'09',
                    'oct.':'10',
                    'okt.':'10',
                    'nov.':'11',
                    'dec.':'12'}
    translator = Translator()
    date_english = translator.translate(date, dest='en').text
    flag = 0
    if 'ago' in date_english:
        # if they are 'some hours/days/minutes/seconds ago'
        flag = 1
        try:
            time_day = date_english.split()[1]
            delta_time = date_english.split()[0]
            if 'hour' in time_day:
                # subtract hours from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(hours=delta_time)).date().strftime("%d/%m/%Y")
            elif 'minute' in time_day:
                # subtract minutes from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(minutes=delta_time)).date().strftime("%d/%m/%Y")
            elif 'second' in time_day:
                # subtract seconds from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(seconds=delta_time)).date().strftime("%d/%m/%Y")
            elif 'day' in time_day:
                # subtract days from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(days=delta_time)).date().strftime("%d/%m/%Y")
        except:
            flag = 0
    
    if len(date_english.split()) == 3:
        # day, month and year all are present
        flag = 1
        actual_date = date_english.split()[0] + '/' + month_to_num[date_english.split()[1]] + '/' + date_english.split()[2]
    
    elif len(date_english.split()) == 2:
        # only month and year are present
        flag = 1
        actual_date = month_to_num[date_english.split()[0]] + '/' + date_english.split()[1]
        
    elif len(date_english.split()) == 1:
        # only year is present
        flag = 1
        actual_date = date_english.split()[0]
        
    else:
        # unidentified date
        actual_date = np.nan
        flag = 0

    # returns datetime format of yyyy-mm-dd
    return pd.to_datetime(actual_date, dayfirst = True)