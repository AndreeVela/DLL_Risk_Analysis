install:
	python3 -m venv .venv &&\
		source .venv/bin/activate &&\
		pip install --upgrade pip &&\
		pip install -r requirements.txt

format: 
	black *.py

lint:
	pylint --disable=R,C hello.py
	
# test:
# 	python -m pytest -vv --cov=hello test
	
all: install lint