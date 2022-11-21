# DLL Adverse Media Analysis
Workspace for working in the intern project

## Setup (Mac OS/Linux)

First, you need to create a new environment using the following commands:

```
# to create the environment
python3 -m venv dll 

# to activate the environnment
source dll/bin/activate
```

Then, you need to run the installation command using make to install dependencies listed in `requirements.txt` file. 

```
make install
```

et voilà! you are ready to go. 


## Setup (Windows)

```
# inside to the project directory DLL_Risk_Analysis, to create a virtual environment
python -m venv .venv

# to active the virtual environment
activate

# installing the requirements.txt file
pip install -r requirements.txt

# running the flask application
flask --app flaskr init-db
flask --app flaskr --debug run
```