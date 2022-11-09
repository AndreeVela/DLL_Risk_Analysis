import numpy as np
import pandas as pd



def generate_google_and_date_ranks( df: pd.DataFrame ):
	"""
	Generates the link ranks based on google search result order and the date. 
	"""
	
	df = df.copy()
	
	# the current order is the google order, so, we let's just create and attribute for that

	google_rank_name = 'Google_rank'
	df.index.name = google_rank_name
	df.reset_index( inplace=True )
	df[ google_rank_name ] = df[ google_rank_name ] + 1
	
	# Sorting by timestamp

	date_rank_name = 'Date_rank'

	temp_df = (df[[ google_rank_name, 'Date' ]]
            .sort_values( by=[ 'Date', 'Google_rank' ] )
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
	