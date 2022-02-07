import os
from dotenv import load_dotenv

# load .env file (linux)

# get parent dir name (path to .env)

# current file path icluding filename (config.py)

curfilePath = os.path.abspath(__file__)

# current directory minus filename

curDir = os.path.abspath(os.path.join(curfilePath, os.pardir))

# parent directory (project folder)

parentDir = os.path.abspath(os.path.join(curDir, os.pardir))

# full path to .env

path_to_env = f'/{parentDir}/.env'

load_dotenv(path_to_env)

CONFIG_CLASS = 'DEV'

if 'DYNO' in os.environ: # DEPLOYED ON HEROKU

    CONFIG_CLASS = 'HEROKU'

    class Config:

        TEMPLATES_AUTO_RELOAD = True
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        
        SQLALCHEMY_TRACK_MODIFICATIONS = False

else: # DEV CLASS

    class Config:

        TEMPLATES_AUTO_RELOAD = True
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

        SQLALCHEMY_TRACK_MODIFICATIONS = False