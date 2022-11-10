# +
# importing necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from googletrans import Translator, constants
import numpy as np

import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
# -

# importing user-defined libraries
from library.link_preprocessor import *



def get_inputFromUI():
    # take input from user
    keywords = "Gerard Sanderink" # make a list
    return keywords


def get_queries():
    keywords = get_inputFromUI()
    
    #read the queries from a file
    with open('data/search_strings.txt', 'r', encoding="utf8") as file:
        queries = file.read().split('\n')
    
    for keyword in keywords:
        replaced_queries = [query.replace("entity", keyword) for query in queries]
    
    print("QUERIES: *******", queries,"\n\n")
    
    return queries
