# DLL Adverse Media Analysis
DLL's adverse media screening process was automated. This project corresponds the period Oct - Nov 2022 of EngD in Data Science program at JADS.

## Recommended Setup

Build and run the project image using docker. The app will run over Gunicorn server inside the container.

![Screenshot 2023-01-09](https://user-images.githubusercontent.com/6290688/212284162-cf7f34a5-2c49-4efc-a353-5f83d1b93ee3.png)


## Manual Setup
The manual setup uses make to install dependencies inside a virtual environment and run the app. However, the app will run in the development server provided by flask.

### For Mac OS / Linux

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


### For Windows

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