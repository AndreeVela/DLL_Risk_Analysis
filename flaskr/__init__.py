import os
import logging
import nltk

from flask import Flask, redirect, url_for
from . import db, search


def create_app(test_config=None):
	nltk.download('stopwords')

	# create and configure the app

	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing

		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in

		app.config.from_mapping(test_config)

	# ensure the instance folder exists

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# a simple page that says hello

	@app.route('/')
	def redirect_to_search():
		return redirect(url_for('search.search'))


	# db.init_app(app)
	app.register_blueprint(search.bp)

	# logging configuration

	logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S')

	app.logger.setLevel(logging.INFO)

	return app