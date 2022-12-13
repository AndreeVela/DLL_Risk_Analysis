import numpy as np
import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer



def generate_google_and_date_ranks( df: pd.DataFrame ):
	"""
	Generates the link ranks based on google search result order and the date. 
	"""
	
	df = df.copy()
	
	# the current order is the google order, so, we let's just create and attribute for that

	google_rank_name = 'Google_rank'
	df[ google_rank_name ] = list( range( 1, df.shape[ 0 ] + 1 ) )
	
	# Sorting by timestamp

	date_rank_name = 'Date_rank'

	temp_df = (df[[ google_rank_name, 'Date' ]]
            .sort_values( by=[ 'Date' ], ascending=False )
            .reset_index( drop=True )
            .drop( columns=[ 'Date' ] ))

	temp_df.index.name = date_rank_name
	temp_df.reset_index( inplace=True )

	df = df.merge( temp_df, how='left', on='Google_rank' )
	
	# selecting columns in the right order
	
	columns = list(df.columns)
	columns.remove( google_rank_name )
	columns.remove( date_rank_name )

	return df[ columns + [ google_rank_name, date_rank_name ] ]



def text_process(msg):
    # 1. all lower case
    # 2. remove punctuation and stopwords
    # 3. lemmatization
    
    msg = msg.lower()
    nopunct = [char for char in msg if char not in string.punctuation]
    nopunct = ''.join(nopunct)
    a = ''
    list_of_words = nopunct.split()
    for i in range(len(list_of_words)):
        if list_of_words[i] not in stopwords.words('english') and list_of_words[i].isalpha():
            b = WordNetLemmatizer().lemmatize(list_of_words[i], pos="v")
            a = a + b + ' '
    a = a.rstrip()
    return a
	