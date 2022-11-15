import datetime
import functools

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


def process_request( entity, country, organization, query_terms, query_string ):
	"""Performes the search"""

	ct = datetime.datetime.now()
	test_article = {
		'title': 'Foobar Article',
		'username': 'John Doe',
		'author_id': '123456',
		'created_at': ct,
		'body': """
				lorem ipsum dolor sit amet, consectetur adipiscing,
				lorem ipsum dolor sit amet, consectetur adipiscing
				lorem ipsum dolor sit amet, consectetur adipiscing
				lorem ipsum dolor sit amet, consectetur adipiscing
				"""
	}

	return [test_article] * 10


@bp.route('/index', methods=('GET', 'POST'))
def search():
	if request.method == 'POST':
		entity = request.form['entity']
		country = request.form['country']
		organization = request.form['organization']
		# query_terms = request.form['search_terms']
		query_terms = request.form.getlist( 'search_terms' )
		query_string = ''

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
					entity, country, organization, ','.join(query_terms), query_string
				),)

				db.commit()
			except db.IntegrityError:
				g.back_to_index = False
				error = f"Error occuried while saving the search in the DB"
				flash(error)
				render_template('search/index.html')
			else:
				search_results = process_request(entity, country, organization, query_terms, query_string)
				g.back_to_index = True

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