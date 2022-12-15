import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as cra
import library.content_analysis as ca
import library.dataframe_preprocessor as dp
import library.doc_similarity as ds
import logging
import pandas as pd
import math
import numpy as np

from datetime import date

logger = logging.getLogger()
URL_PREFIX = 'https://google.com/search?q='
N_HITS = 20

def process_request( query_terms, country=None):
	"""Performes the search"""

	query_terms = query_terms if not country else query_terms + [ country ]
	query_strings, keyword_mapper, adverse_type_mapper = qb.get_queries(query_terms)

	# Declaring what is scaraped from results

	final_hits_df = pd.DataFrame()

	# iterate over every query

	indexer = 0
	for query in query_strings:
		logger.info( f"Crawling query {indexer + 1}" )
		hits_df = wc.get_hitsinformation(URL_PREFIX + query, query_terms)
		hits_df['Target Search'] = keyword_mapper[indexer]
		hits_df['Adverse Type'] = adverse_type_mapper[indexer]
		indexer += 1
		final_hits_df = final_hits_df.append(hits_df)

	# credibility analysis (1 -> HIGHEST, 3 -> LOWEST)

	logger.info( 'Credibility Scorer' )
	final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(cra.score)

	# relevancy analysis (< 5 years: 'Recency' = 1 and 0 otherwise)

	logger.info( 'Recency Assessment' )
	final_hits_df['Recency'] = final_hits_df['Date'].map(lambda date: 1 if (date.today().year - date.year) <= 5 else 0)

	# performing content analysis for non-social media sources
	## creating a new columns, 'heading' and 'content' to get the content for non-Social Media sources

	logger.info( 'Content analysis for non-social-media sources' )
	heading_content_df = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'URL'].apply(ca.extractor)
	headings = [heading_content[0] for heading_content in list(heading_content_df)]
	contents = [heading_content[1] for heading_content in list(heading_content_df)]

	final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Heading'] = headings
	final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'] = contents

	# measuring the adversity score for each and every content

	logger.info( 'Adversity Scoring' )
	final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Adversity Score'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'].apply(ca.adversity)

	# create google and data rank attributes

	final_hits_df = dp.generate_google_and_date_ranks(final_hits_df)
	final_hits_df.sort_values(inplace=True, by=['Google_rank'])

	# document similarity and reliability analysis
	final_hits_df_notsocialmedia = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media']
	final_hits_df_notsocialmedia = final_hits_df_notsocialmedia[final_hits_df_notsocialmedia['Source Type'].notna()]
	final_hits_df_notsocialmedia = final_hits_df_notsocialmedia[final_hits_df_notsocialmedia['Content'].notna()]

	final_hits_df_notsocialmedia['Preprocessed Content'] = final_hits_df_notsocialmedia['Content'].apply(dp.text_process)
	doc_similarity_df = ds.pairwise_doc_similariy(list(final_hits_df_notsocialmedia['URL']), list(final_hits_df_notsocialmedia['Content']))

	avg_doc_similarity_scores = ds.compute_avg_similarity(np.array(doc_similarity_df))

	final_hits_df_notsocialmedia['Reliability Score'] = avg_doc_similarity_scores
	final_hits_df_notsocialmedia = final_hits_df_notsocialmedia[['URL', 'Reliability Score']]

	final_hits_df = pd.merge(final_hits_df, final_hits_df_notsocialmedia, on = 'URL', how = 'outer')
	final_hits_df.drop_duplicates(inplace = True)

	return final_hits_df, query_strings



def stratified_sampling(final_hits_df: pd.DataFrame):
	"""
	Performs a stratified sampling based on year quartiles.
	"""

	hits_data = (final_hits_df
				 .sort_values(by=['Date','Adversity Score'])
				 .groupby(pd.Grouper(key='Date', freq="QS"))
				 .apply(lambda x: x)
				 .sort_values(by=['Date','Adversity Score'], ascending = [False, False]))

	hits_data[ 'year_quarter' ] = hits_data.Date.dt.to_period('Q')

	proportion = N_HITS / len( hits_data )
	quarters_sampling_size_df = hits_data.groupby( "year_quarter" ).apply( lambda x: math.ceil(len(x) * proportion) )

	top_hits = ( (
			hits_data
				.groupby( "year_quarter", as_index=False )
				.apply( lambda x: x.head( quarters_sampling_size_df[ x.year_quarter.iloc[0] ] ) )
				.sort_values( by="year_quarter", ascending=False )
				.set_index( "year_quarter" ) )
		.reset_index()
		.drop('year_quarter', axis = 1)
	)

	return top_hits

