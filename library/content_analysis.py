# importing necessary libraries
import requests
from bs4 import BeautifulSoup
import re
from googletrans import Translator, constants
import numpy as np

# importing user-defined libraries
from library.link_preprocessor import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from library.web_crawler import get_soup


# extracts the content in English
def extractor(url):
    # getting the soup object
    soup = get_soup(url)

    # getting the paragraph soup
    search_data = soup.find_all('p')

    # getting the heading soup
    search_data_heading = soup.find_all('h1')
    try:
        article_heading = search_data_heading[0].text
    except:
        article_heading = ''

    # extracting and preprocessing the content
    text = [re.sub(' +', ' ', search_data[i].text) for i in range(0, len(search_data))]
    text = ' '.join(text)
    text = re.sub('[\r\n\t]+',' ', text)
    list_of_lines = text.strip().split('.')
    ## stopping content extraction when encountering an empty string
    try:
    	text = list_of_lines[1:list_of_lines.index('')]
    	text = article_heading + ' ' + '.'.join(text)
    	text = re.sub(' +', ' ', text)
    except:
    	text = article_heading + ' ' + text
    	text = re.sub(' +', ' ', text)
        
    text = text.strip()

    
    # translating content in any language to English
    #translator = Translator()
    #text = translator.translate(text, dest='en').text

    if article_heading == '':
        article_heading = text.split('.')[0].strip()

    return article_heading, text


# checking whether any keyword is present in the content
def entity_check(text, keywords_list):
	flag = 0
	for keyword in keywords_list:
		if keyword in text:
			flag = 1
			break

	# if no keyword is present in the content
	if flag == 0:
		return flag

	# if a keyword is found in the content
	else:
		return flag


# sentiment/adversity analysis
def adversity(text):
	analyzer = SentimentIntensityAnalyzer()
	polarity_analysis = analyzer.polarity_scores(text)
	compound_score = polarity_analysis['compound']
	if compound_score < 0:
		return -compound_score
	else:
		return polarity_analysis['neg']
