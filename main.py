import library.content_analysis as ca
import library.credibility_analysis as cra
import library.dataframe_preprocessor as dp
import library.doc_similarity as ds
import library.link_preprocessor as lp
import library.pipeline as pipeline
import library.query_builder as qb
import library.web_crawler as wc
import logging
import pandas as pd
import numpy as np

from datetime import date

logger = logging.getLogger()

if __name__ == "__main__":
	logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S')
	logging.getLogger().setLevel(logging.INFO)


	## input comes from UI, maybe a list of inputs, modify code later
	## contacting google with search string is done in nested loop

	keywords_list = qb.get_inputFromUI()
	search_results, query_strings = pipeline.process_request(keywords_list, '')

	# top max 50 sources or URLs of Adverse Media
	## picking the news that are related for the last five years

	top_hits_df = search_results.loc[search_results['Recency'] == 1]
	top_hits_df.sort_values(by=['Date', 'Adversity Score'], inplace=True, ascending = [False, False])
	top_hits_df = top_hits_df.head(40)

	'''
	# document similarity and reliability analysis
	top_hits_df_notsocialmedia = top_hits_df.loc[top_hits_df['Source Type'] != 'Social Media']
	top_hits_df_notsocialmedia = top_hits_df_notsocialmedia[top_hits_df_notsocialmedia['Source Type'].notna()]
	top_hits_df_notsocialmedia = top_hits_df_notsocialmedia[top_hits_df_notsocialmedia['Content'].notna()]

	top_hits_df_notsocialmedia['Preprocessed Content'] = top_hits_df_notsocialmedia['Content'].apply(dp.text_process)
	doc_similarity_df = ds.pairwise_doc_similariy(list(top_hits_df_notsocialmedia['URL']), list(top_hits_df_notsocialmedia['Content']))

	avg_doc_similarity_scores = ds.compute_avg_similarity(np.array(doc_similarity_df))

	top_hits_df_notsocialmedia['Reliability Score'] = avg_doc_similarity_scores

	top_hits_df = pd.merge(top_hits_df, top_hits_df_notsocialmedia, on = 'URL', how = 'outer')
	top_hits_df.drop_duplicates(inplace = True)
	'''

	print('Adverse Media Screened !!!')
	search_results.to_excel('AMS.xlsx', index = False)
	top_hits_df.to_excel('AMS_tophits.xlsx', index = False)
