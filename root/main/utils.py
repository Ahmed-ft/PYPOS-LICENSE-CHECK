# convert UTC to local time (UTC+2) (modules)

from datetime import datetime
from pytz import timezone

# random string (modules)

import re
import uuid
import base64
import pytz

# token auth

from functools import wraps
from flask import jsonify, request
from root.config import Config
import jwt

# create user

def create_user(username, passwd):

    try:

        from root.main.models import User
        from root import bcrypt, db

        passwd = passwd
        hashed_password = bcrypt.generate_password_hash(
            passwd).decode("utf-8")

        user = User(username=username, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        print(f'CREATING USER <{ username }> >> DONE')

        all_users = User.query.all()

        print('LIST OF USERS: ')

        for user in all_users:

            print(f'{user.username}')

    except Exception as e:

        print(e)
        return e

# take input from user

def take_input(question):

    reply = str(input(question+' y / n : ')).lower().strip()
    
    if reply[0] == 'y':
        
        return True

    if reply[0] == 'n':
        
        return False

# drop db table

def drop_tbl(class_name, app):
    """

    drop_tbl() >> drop a table from database

    :param1 class_name: class name mapped to table (CASE SENSITIVE).
    :param2 app: the application object (app=create_app()) to push app context.

    workflow :

    this function passes <class_name> to getattr(<module>, <class_name>) to create instance of class
    then drops table using <instance_of_model_class>.__table__.drop(<obj:db_engine>) method
    which takes db engine as argument.

    - import module (models.py module) with importlib.import_module(<string:path.to.module>) method
    - create object of class using getattr(<obj:module>, <string:class_name>)
    - create instance of class (cant use anything other than instance of class) by adding
    () to the class object

    return : no return

    """

    try:

        import importlib
        from root import db

        app.app_context().push()

        print('\n')
        print(f'DROPPING TABLE <{ class_name }>')
        print('\n')

        module = importlib.import_module("root.blueprint.models")
        class_ = getattr(module, class_name)
        instance = class_()

        instance.__table__.drop(db.engine)

        print(f'TABLE <{ class_name }> DROPPED SUCCESSFULLY.')
        print('\n')

    except Exception as e:

        print('From Exception: ')
        print('\n')
        print(e)
        print('\n')

        print(f'FAILED TO DROP TABLE <{ class_name }>')

# api token auth

def generate_auth_token():

    try:

        import datetime

        token = jwt.encode({'user': 'license_check_api', 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(seconds=9999)}, Config.SECRET_KEY)

        return token

    except Exception as e:

        return e


def auth_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # # http://127.0.0.1:5000/route?t=<auth_token>
        token = request.args.get('t')

        if not token:

            return jsonify({'message': 'Token is missing!'}), 403

        try:

            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

        except:

            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

# random string (very unique)


def uuid_url64():

    rv = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
    return re.sub(r'[\=\+\/]', lambda m: {'+': '-', '/': '_', '=': ''}[m.group(0)], rv)

# convert UTC to local time (UTC+2)


def localTime():

    tz = timezone('Africa/Cairo')
    utc = datetime.utcnow()
    local = pytz.utc.localize(utc, is_dst=None).astimezone(tz)

    return local