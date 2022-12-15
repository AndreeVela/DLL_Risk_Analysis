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
    #translator = Translator()
    #headline = translator.translate(headline, dest='en').text
    return headline


def date_checker(text):
    # checking whether a 4-digit year or not
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
                    'maart':'03',
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
            delta_time = int(date_english.split()[0])
            if 'hour' in time_day or 'hr' in time_day:
                # subtract hours from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(hours=delta_time)).date().strftime("%d/%m/%Y")
            elif 'minute' in time_day or 'min' in time_day:
                # subtract minutes from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(minutes=delta_time)).date().strftime("%d/%m/%Y")
            elif 'second' in time_day or 'sec' in time_day:
                # subtract seconds from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(seconds=delta_time)).date().strftime("%d/%m/%Y")
            elif 'day' in time_day:
                # subtract days from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(days=delta_time)).date().strftime("%d/%m/%Y")
            elif 'week' in time_day:
                # subtract weeks from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(weeks=delta_time)).date().strftime("%d/%m/%Y")
            elif 'month' in time_day:
                # subtract months = months * (1 month = 4 weeks) from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(weeks=delta_time*4)).date().strftime("%d/%m/%Y")
            elif 'year' in time_day:
                # subtract years = years * (1 year = 52 weeks) from real-time and get the date
                actual_date = (pd.Timestamp.now() - pd.Timedelta(weeks=delta_time*52)).date().strftime("%d/%m/%Y")
        except:
            flag = 0
    
    else:
        # it is an explicit date, so the format needs to be checked
        date_check_list = date_english.split()
        if len(date_check_list) >= 2 and date_check_list[0].isnumeric() == False:
            # if month comes first ....
            date_english = date_english.split()[1].strip(',') + ' ' + date_english.split()[0] + ' ' + date_english.split()[2]

        if len(date_english.split()) == 3:
            # day, month and year all are present
            flag = 1
            try:
                actual_date = date_english.split()[0] + '/' + month_to_num[date_english.split()[1][:3].lower().strip(',')] + '/' + date_english.split()[2]
            except:
                actual_date = date_english.split()[0] + '/' + month_to_num[date_english.split()[1][:3].lower() + '.'.strip(',')] + '/' + date_english.split()[2]
        
        elif len(date_english.split()) == 2:
            # only month and year are present
            flag = 1
            try:
                actual_date = month_to_num[date_english.split()[0][:3].lower().strip(',')] + '/' + date_english.split()[1]
            except:
                actual_date = month_to_num[date_english.split()[0][:3].lower() + '.'.strip(',')] + '/' + date_english.split()[1]

            
        elif len(date_english.split()) == 1:
            # only year is present
            flag = 1
            actual_date = date_english.split()[0].strip(',')
            
        else:
            # unidentified date
            actual_date = np.nan
            flag = 0

    return pd.to_datetime(actual_date, dayfirst = True)


# identifying the type of source (newspaper/journal/social media)
def source_type_identifier(source, news):
    if news == 1:
        return 'Newspaper/Magazine'
    elif news == 0:
        flag = 0
        list_of_social_media = ['facebook', 'fb', 
                                'instagram',
                                'youtube',
                                'twitter',
                                'reddit',
                                'linkedin',
                                'pinterest',
                                'tumblr']

        for social_media in list_of_social_media:
            if social_media in source:
                flag = 1
                return 'Social Media'

        if flag == 0:
            return 'Investigative Journal'


# if the URL is actually taken from the home page of the entity (company website), then it is neither a newspaper nor journal nor social media
def entity_source_check(source, keywords_list):
    flag = 0
    for keyword in keywords_list:
        if (keyword.lower() in source) or (source in keyword.lower()):
            flag = 1
            return False

    if flag == 0:
        return True
