import os
import logging
import nltk

from flask import Flask, redirect, url_for
from . import db, search


def create_app(test_config=None):
	# logging configuration

	logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S')

	logger = logging.getLogger()

	# create and configure the app

	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY = 'dev',
		DATABASE = os.path.join( app.instance_path, 'flaskr.sqlite' ),
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
		return redirect(url_for( 'search.search' ))

	app.register_blueprint( search.bp )
	app.logger.setLevel( logging.INFO )

	logger.info( 'Downloading stopwords' )
	nltk.download( [ 'stopwords', 'wordnet' ] )
	logger.info( f"File location: {os.path.realpath(os.path.dirname(__file__))}" )

	nltk.data.path.append( '../nltk_data/' )
	logger.info( f'nltk data after: {nltk.data.path}' )

	return app