import library.content_analysis as ca
import library.credibility_analysis as cra
import library.dataframe_preprocessor as dp
import library.doc_similarity as ds
import library.link_preprocessor as lp
import library.pipeline as pipeline
import library.query_builder as qb
import library.web_crawler as wc
import logging
import nltk
import numpy as np
import pandas as pd

from datetime import date

logger = logging.getLogger()

if __name__ == "__main__":
	logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S')
	logging.getLogger().setLevel(logging.INFO)

	nltk.download(['stopwords', 'wordnet'])

	## input comes from UI, maybe a list of inputs, modify code later
	## contacting google with search string is done in nested loop

	keywords_list = qb.get_inputFromUI()
	search_results, query_strings = pipeline.process_request(keywords_list, '')

	print('Adverse Media Screened !!!')
	search_results.to_excel('./output/AMS.xlsx', index = False)
