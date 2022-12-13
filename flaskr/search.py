import datetime
import functools
import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as cra
import library.content_analysis as ca
import library.dataframe_preprocessor as dfp
from flask import current_app as app
import pandas as pd

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


def process_request( query_terms, country=None):
	"""Performes the search"""

	query_terms = query_terms if not country else query_terms + [ country ]
	query_strings = qb.get_queries(query_terms)
	query_strings, keyword_mapper, adverse_type_mapper = qb.get_queries()

	# Declaring what is scaraped from results

	final_hits_df = pd.DataFrame()
	url_prefix = 'https://google.com/search?q='

	# iterate over every query

	indexer = 0
	for query in query_strings:
		app.logger.info( f"Crawling query {indexer + 1}" )
		hits_df = wc.get_hitsinformation(url_prefix + query, query_terms)
		hits_df['Target Search'] = keyword_mapper[indexer]
		hits_df['Adverse Type'] = adverse_type_mapper[indexer]
		indexer += 1
		final_hits_df = final_hits_df.append(hits_df)

	# credibility analysis (1 -> HIGHEST, 3 -> LOWEST)

	app.logger.info( 'Credibility Scorer' )
	final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(cra.score)

	# relevancy analysis (< 5 years: 'Recency' = 1 and 0 otherwise)

	app.logger.info( 'Recency Assessment' )
	final_hits_df['Recency'] = final_hits_df['Date'].map(lambda date: 1 if (date.today().year - date.year) <= 5 else 0)

	# performing content analysis for non-social media sources
	## creating a new columns, 'heading' and 'content' to get the content for non-Social Media sources

	app.logger.info( 'Content analysis for non-social-media sources' )
	heading_content_df = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'URL'].apply(ca.extractor)
	headings = [heading_content[0] for heading_content in list(heading_content_df)]
	contents = [heading_content[1] for heading_content in list(heading_content_df)]

	final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Heading'] = headings
	final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'] = contents

	# measuring the adversity score for each and every content

	app.logger.info( 'Adversity Scoring' )
	final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Adversity Score'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'].apply(ca.adversity)
	
	# create google and data rank attributes

	final_hits_df = dfp.generate_google_and_date_ranks(final_hits_df)
	final_hits_df.sort_values(inplace=True, by=['Google_rank'])
	
	return final_hits_df.to_dict('records'), query_strings


@bp.route('/', methods=('GET', 'POST'))
def search():
	if request.method == 'POST':
		entity = request.form['entity'] if request.form['entity'] else ''
		# country = request.form['country'] if request.form['country'] else ''

		if 'search_terms' in request.form.keys():
			query_terms = request.form.getlist( 'search_terms' )
		else:
			query_terms = []

		query_terms = [entity] + query_terms
		app.logger.info('Query terms: %s', query_terms)

		db = get_db()
		error = None

		# validate null fields

		# if not entity or not country or not query_terms:
		if not entity:
			error = 'You need to provide an entity'

		if error is None:

			# saving the query

			# try:
			# 	db.execute((
			# 		"INSERT INTO searchs (entity, country, organization, query_terms, query_string) "
			# 		"VALUES (?, ?, ?, ?, ?)"
			# 	),(
			# 		entity, '', '', '', ''
			# 	),)

			# 	db.commit()
			# except db.IntegrityError:
			# 	g.back_to_index = False
			# 	error = f"Error occuried while saving the search in the DB"
			# 	flash(error)
			# 	render_template('search/index.html')
			# else:

			search_results, query_strings = process_request(query_terms, '')
			g.back_to_index = True

			return render_template('search/results.html', entity=entity, country='', organization='',
				query_terms=query_terms, query_strings=query_strings, search_results=search_results)
		else:
			flash(error)

	return render_template('search/index.html')



@bp.route('/download', methods=('GET', 'POST'))
def download():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		error = None
		user = db.execute(
			'SELECT * FROM user WHERE username = ?', (username,)
		).fetchone()

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user['password'], password):
			error = 'Incorrect password.'

		if error is None:
			session.clear()
			session['user_id'] = user['id']
			return redirect(url_for('index'))

		flash(error)

	return render_template('auth/login.html')