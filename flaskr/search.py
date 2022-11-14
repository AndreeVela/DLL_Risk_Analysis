import functools

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


def process_request( entity, country, query_terms, query_string ):
	"""Performes the search"""
	pass


@bp.route('/index', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		entity = request.form['entity']
		country = request.form['country']
		query_terms = request.form['query_terms']
		query_string = ''

		db = get_db()
		error = None

		# validate null fields

		if not entity or not country or not query_terms:
			error = 'You need to provide an entity, country, and query terms'

		if error is None:

			# saving the query

			try:
				db.execute(
					"INSERT INTO searchs (entity, country, query_terms, query_string) VALUES (?, ?, ?, ?)",
					(entity, country, query_terms, query_string),
				)
				db.commit()
			except db.IntegrityError:
				error = f"Error occuried while saving the search in the DB"
			else:
				return redirect(url_for("search.results"))

			# performingn the search

			search_results = process_request(entity, country, query_terms, query_string)
			render_template('search/results.html', entity=entity, country=country,
				query_terms=query_terms, query_string=query_string, search_results=search_results)

		flash(error)

	return render_template('search/index.html')



@bp.route('/download', methods=('GET', 'POST'))
def login():
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