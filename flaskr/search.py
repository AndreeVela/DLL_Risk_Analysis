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


def process_request( entity, country, organization, query_terms ):
	"""Performes the search"""
    
    # read the queries from a file
	with open('./flaskr/queries/search_strings.txt',  encoding='utf-8') as f:
		query_strings = f.readlines()
    
    # Declaring what is scaraped from results
	final_hits_df = pd.DataFrame()
    
	url_prefix = 'https://google.com/search?q='

    # iterate over every query
	for query in query_strings:
		hits_df = wc.get_hitsinformation(url_prefix + query.replace('entity', entity), query_terms)
		final_hits_df = final_hits_df.append(hits_df)

    # credibility analysis (1 -> HIGHEST, 3 -> LOWEST)
	final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(ca.score)
	
	# create google and data rank attributes
	print('DF size', final_hits_df.shape)
	final_hits_df = dfp.generate_google_and_date_ranks(final_hits_df)
	final_hits_df.sort_values(inplace=True, by=['Google_rank'])
	print('DF size', final_hits_df.shape)

	
	return final_hits_df.to_dict('records'), query_strings


@bp.route('/index', methods=('GET', 'POST'))
def search():
	if request.method == 'POST':
		entity = request.form['entity']
		country = request.form['country']
		organization = request.form['organization']
		# query_terms = request.form['search_terms']
		query_terms = request.form.getlist( 'search_terms' )

		db = get_db()
		error = None

		# validate null fields

		if not entity or not country or not query_terms:
			error = 'You need to provide an entity, country, and query terms'

		if error is None:

			# saving the query

			try:
				db.execute((
					"INSERT INTO searchs (entity, country, organization, query_terms, query_string) "
					"VALUES (?, ?, ?, ?, ?)"
				),(
					entity, country, organization, ','.join(query_terms), ''
				),)

				db.commit()
			except db.IntegrityError:
				g.back_to_index = False
				error = f"Error occuried while saving the search in the DB"
				flash(error)
				render_template('search/index.html')
			else:
				search_results, query_string = process_request(entity, country, organization, query_terms)
				g.back_to_index = True

				print( type(search_results) )
				print(search_results)

				return render_template('search/results.html', entity=entity, country=country, organization=organization,
					query_terms=', '.join(query_terms), query_string=query_string, search_results=search_results)
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