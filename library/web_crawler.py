# importing necessary libraries
import requests
import bs4
import pandas as pd
import re
import numpy as np
import library.link_preprocessor as lp
import warnings
warnings.filterwarnings('ignore')



# getting the soup from query url
def get_soup(query_url):
    headers = {"Accept-Language": "en,en-NL", 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request = requests.get(query_url, headers=headers, cookies=cookies)
    
    soup = bs4.BeautifulSoup(request.text,'html.parser')
    return soup


def getGoogleNewsURL(soup):
    topbarlinks = soup.find_all("div", {"class" : "hdtb-mitem"})
    
    ##Get the second item in google links
    i=0
    for link in topbarlinks:
        i=i+1
        if i==2:
            news_tag = link
            news_link = "https://google.com"+news_tag.find('a')['href']
            break

    return news_link


# the master function giving the output dataframe for each and every query url
def get_hitsinformation(query_url, keywords_list):
    
    # getting soup of the 'All' page
    all_soup = get_soup(query_url)
    
    # getting the URL of the 'News' tab from the soup of the 'All' page 
    news_url = getGoogleNewsURL(all_soup)
    # getting the soup of the 'News' tab from the URL of the 'News' tab
    news_soup = get_soup(news_url)
    
    # all_hits is a dictionary of structure: {'URL': [], 'Date' : []}
    all_hits = search_google_all(all_soup)
    ##print("ALL HITS:\n", len(all_hits['URL']))

    # news_hits is a dictionary of structure: {'URL': [], 'Date' : []}
    news_hits = search_google_news(news_soup)
    ##print("\n\nNEWS HITS:\n", len(news_hits['URL']))
    
    # final dataframe (left join of [all, news])
    all_hits_df = pd.DataFrame(all_hits)
    
    news_hits_df = pd.DataFrame(news_hits)
    news_hits_df['NEWS'] = 1
    
    all_and_news_df = pd.merge(all_hits_df, news_hits_df, on = ['URL', 'Date'], how = 'outer')
    all_and_news_df['NEWS'].fillna(0, inplace = True)
    
    # processing the Date from the URL
    all_and_news_df['Date'] = all_and_news_df['Date'].apply(lp.date_processor)
    
    # getting the Source, Source Type and Headline from the URL
    all_and_news_df['Source'] = all_and_news_df['URL'].apply(lp.extract_sourcename)

    all_and_news_df['Source Type'] = np.vectorize(lp.source_type_identifier)(all_and_news_df['Source'], all_and_news_df['NEWS'])
    all_and_news_df['Source Type Check'] = all_and_news_df['Source'].apply(lp.entity_source_check, args = (keywords_list,))
    all_and_news_df.loc[all_and_news_df['Source Type Check'] == False, 'Source Type'] = ''

    #all_and_news_df['Heading'] = all_and_news_df['URL'].apply(lp.extract_headline)

    # removing the 'NEWS' and 'Source Type Check' columns as it does not make sense anymore....
    all_and_news_df.drop(['NEWS', 'Source Type Check'], axis = 1, inplace = True)

    
    return all_and_news_df



def search_google_all(soup):
    all_search_dict = {'URL': [], 'Date' : []}
    # getting all the google searches and related data
    search_data = soup.find_all("div", {"class" : "g"})
    
    # pagination and scraping in progress
    page_no = 1
    while(1):
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
                    if lp.date_checker(text_element):
                        date = text_element
                        break
            except:
                ## if no search date can be found...
                date = ""

            all_search_dict['Date'].append(date)

        ## navigating to the next page and scraping the subsequent google search URLs
        try:
            search_page = "Page " + str(page_no + 1)
            search_url = soup.find("a", {"aria-label" : search_page}).get("href")
            r = requests.get("https://www.google.com" + search_url, headers = headers)
            c = r.text
            soup = BeautifulSoup(c, "html.parser")
            search_data = soup.find_all("div", {"class" : "g"})
        except:
            # no more pages
            break

    return all_search_dict


## Scrape from Google News Tab
def search_google_news(soup):
    news_search_dict = {'URL': [], 'Date' : []}
    heading_list = []
    date_list = []
    url_list = []
    
#    page_no = 2
    for page_no in range(2,10):
#    while(1):
        try:
            heading_list.extend([e.get_text(strip=True) for e in soup.find_all('div', {"role":"heading"})])
            date_list.extend([e.get_text(strip=True) for e in soup.find_all('div', {"class": "OSrXXb ZE0LJd YsWzw"})])
            url_list.extend([e.get("href") for e in soup.find_all("a",{"class":"WlydOe"})])
    
            search_page = "Page " + str(page_no)
            search_url = soup.find("a", {"aria-label" : search_page}).get("href")
            soup = get_soup("https://www.google.com" + search_url)
            ## print("\n\n\n***SOUP")
        except:
            break
    
    # print("\n\n\n\n***headings: ",len(heading_list),"\n",heading_list)
    # print("\n\n\n\n***date: ",len(date_list),"\n",date_list)
    # print("\nURL:",len(url_list),"\n", url_list)
    
    news_search_dict['URL'] = url_list
    news_search_dict['Date'] = date_list
    ## print("\n\nNEWS SEARCH DICT:\n", news_search_dict)
    return news_search_dict


# def search_google(soup, n_pages):
#     all_search_dict = {'URL': [], 'Date' : []}
#     # getting all the google searches and related data
#     search_data = soup.find_all("div", {"class" : "g"})    

#     # scraping all the search links appearing in the number of pages requested in the input    
#     for page_no in range(1, n_pages):
#         n_searches = len(search_data)
#         for search in range(n_searches):
#             search_result = search_data[search]
#             ## getting the search URL
#             url = search_result.find("a").get("href")
#             all_search_dict['URL'].append(url)

#             try:
#                 ## trying to get the search date
#                 date_section = search_result.find('span', {"class":"MUxGbd wuQ4Ob WZ8Tjf"}).find_all('span')
#                 for element in date_section:
#                     text_element = element.text
#                     if lp.date_checker(text_element):
#                         date = text_element
#                         break
#             except:
#                 ## if no search date can be found...
#                 date = ""

#             all_search_dict['Date'].append(date)

#         ## navigating to the next page and scraping the subsequent google search URLs
#         try:
#             search_page = "Page " + str(page_no + 1)
#             search_url = soup.find("a", {"aria-label" : search_page}).get("href")
#             r = requests.get("https://www.google.com" + search_url, headers = headers)
#             c = r.text
#             soup = BeautifulSoup(c, "html.parser")
#             search_data = soup.find_all("div", {"class" : "g"})
#         except:
#             # no more pages found
#             break

#         return all_search_dict
