import datetime
import functools
import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as ca
import library.dataframe_preprocessor as dfp
import pandas as pd

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


def process_request( entity, country=None, organization=None ):
	"""Performes the search"""
    
    # read the queries from a file
	# with open('./flaskr/queries/search_strings.txt',  encoding='utf-8') as f:
	# 	query_strings = f.readlines()
	# [entity], './flaskr/queries/search_strings.txt'

	query_terms = [ entity ]
	query_terms = query_terms if not organization else query_terms + [ organization ]
	query_terms = query_terms if not country else query_terms + [ country ]

	query_strings = qb.get_queries([entity])
    
    # Declaring what is scaraped from results
	final_hits_df = pd.DataFrame()
    
	url_prefix = 'https://google.com/search?q='

    # iterate over every query
	for query in query_strings:
		hits_df = wc.get_hitsinformation(url_prefix + query, query_terms)
		final_hits_df = final_hits_df.append(hits_df)

    # credibility analysis (1 -> HIGHEST, 3 -> LOWEST)
	final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(ca.score)
	
	# create google and data rank attributes
	final_hits_df = dfp.generate_google_and_date_ranks(final_hits_df)
	final_hits_df.sort_values(inplace=True, by=['Google_rank'])
	
	return final_hits_df.to_dict('records'), query_strings


@bp.route('/index', methods=('GET', 'POST'))
def search():
	if request.method == 'POST':
		entity = request.form['entity'] if request.form['entity'] else ''
		# country = request.form['country'] if request.form['country'] else ''

		if 'search_terms' in request.form.keys():
			query_terms = request.form.getlist( 'search_terms' )
		else:
			query_terms = []
		print(query_terms)

		db = get_db()
		error = None

		# validate null fields

		# if not entity or not country or not query_terms:
		if not entity:
			error = 'You need to provide an entity'

		if error is None:

			# saving the query

			try:
				db.execute((
					"INSERT INTO searchs (entity, country, organization, query_terms, query_string) "
					"VALUES (?, ?, ?, ?, ?)"
				),(
					entity, '', '', '', ''
				),)

				db.commit()
			except db.IntegrityError:
				g.back_to_index = False
				error = f"Error occuried while saving the search in the DB"
				flash(error)
				render_template('search/index.html')
			else:
				search_results, query_strings = process_request(entity, '', '')
				g.back_to_index = True

				return render_template('search/results.html', entity=entity, country='', organization='',
					query_terms=', '.join([]), query_strings=query_strings, search_results=search_results[:20])
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