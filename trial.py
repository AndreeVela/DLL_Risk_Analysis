# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 14:37:24 2022

@author: 20215649
"""
# Import the beautifulsoup 
# and request libraries of python.
import requests
import bs4
import time





def getGoogleNewsURL():
    text= "geeksforgeeks"
    url = 'https://google.com/search?q=' + text
    headers = {"Accept-Language": "en,en-NL", 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    #headers = {"Accept-Language": "en,en-NL", 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    html =requests.get( url ,headers=headers, cookies=cookies)
     
    # Creating soup from the fetched request
    soup = bs4.BeautifulSoup(html.content,'html.parser')
    #print(soup)
    links = soup.find_all("div", {"class" : "hdtb-mitem"})
   
    ##Get the second item in google links
    i=0
    for link in links:
        i=i+1
        if i==2:
            news_tag = link
            news_link = "https://google.com"+news_tag.find('a')['href']
            break

    ## Get the href tag of child(a)
    return news_link

if __name__ == "__main__":
# Make two strings with default google search URL
# 'https://google.com/search?q=' and
# our customized search keyword.
# Concatenate them
    news_url = getGoogleNewsURL()
    print(news_url)
    headers = {"Accept-Language": "en,en-NL", 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    
    request =requests.get(news_url,headers=headers, cookies=cookies)
    
    soup = bs4.BeautifulSoup(request.text,'html.parser')
    #print(soup.prettify()[40000:90000])
    print("*******")
    
    #Get the news headings
    headings = soup.find_all("div", {"role":"heading"})
    ## take the tiles into a dataframe
    print(headings[0].contents[0])
    print("\n*******")
    #But we need to find the news headings in sync with all other items
    #So start at the beginning and go in order
    # Generic approach to it
    
    outer_div = soup.find_all("div", {"class":"MjjYud"})
    print(outer_div.findChild())
    
    
    
    
    
    
    
    
    
    # ## input comes from UI, maybe a list of inputs, modify code later
    # ## contacting goole with search string is done in loop
    # input = "Gerard Sanderink" 
    # #read the queries from a file
    # with open('data/search_strings.txt', 'r', encoding="utf8") as file:
    #     queries = file.read().split('\n')

    # links = []
    # for query in queries:
    #     query = query.replace("entity", input)
    #     print(query)
    # #     links.append(scrape_google(query))
    # # links = scrape_google(query)
    # # print(links)
    
