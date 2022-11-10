## make requirements.txt file
from urllib import response
import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import requests
import bs4
import time

def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response
    except requests.exceptions.RequestException as e:
        print(e)
        
# https://practicaldatascience.co.uk/data-science/how-to-scrape-google-search-results-using-python
def OLDscrape_google(query):
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)
    hits = list(response.html.absolute_links)
    
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            hits.remove(url)    
    return hits

def search_google(query):
    url = 'https://google.com/search?q=' + query
    headers = {"Accept-Language": "en,en-NL", 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request =requests.get(url,headers=headers, cookies=cookies)
    
    soup = bs4.BeautifulSoup(request.text,'html.parser')
    # print(soup.prettify()[40000:90000])
    print("\n\nsoup ready *******")
    
    #Get the news headings
    headings = soup.find_all("div", {"role":"heading"})
    ## take the tiles into a dataframe
    print(headings[0].contents[0])
    print("\n*******")
    
    


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


def get_inputFromUI():
    
    keywords="Gerard Sanderink" # make a list
    return keywords



if __name__ == "__main__":
    ## input comes from UI, maybe a list of inputs, modify code later
    ## contacting google with search string is done in nested loop
    input = get_inputFromUI() 
    
    #read the queries from a file
    with open('data/search_strings.txt', 'r', encoding="utf8") as file:
        queries = file.read().split('\n')
    print("QUERIES: *******", queries,"\n\n")
    links = []
    for query in queries:
        query = query.replace("entity", input)
        print("\n\nQuery:", query," \n\n")
        search_google(query)
        # links.append(OLDscrape_google(query))
        # links.append("*************")
        
        # print(links)
        # print(len(links))
        # links = scrape_google(query)
    