import pandas as pd

def score(source_type):
	if source_type == 'Newspaper/Magazine' or source_type == '':
		return 1
	elif source_type == 'Investigative Journal':
		return 2
	elif source_type == 'Social Media':
		return 3