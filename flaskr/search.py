import datetime
import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as cra
import library.content_analysis as ca
import library.dataframe_preprocessor as dfp
import library.pipeline as pipeline
from flask import current_app as app
import pandas as pd

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


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

		error = None
		if not entity:
			error = 'You need to provide an entity'

		if error is None:
			search_results, query_strings = pipeline.process_request(query_terms, '')
			search_results = pipeline.stratified_sampling( search_results )
			g.back_to_index = True

			return render_template('search/results.html', entity=entity, country='', organization='',
				query_terms=query_terms, query_strings=query_strings, search_results=search_results.to_dict('records'))
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