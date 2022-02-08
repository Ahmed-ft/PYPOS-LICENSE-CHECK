from functools import wraps # FOR DECORATORS.


# PRINT EXCEPTION MESSAGE

def print_exception(e):

    print('\n')
    print(f'*Exception* ----> { e }')
    print('\n')

# CRUD DATABASE.

class CrudDatabase:

    def create_database(self, db_name):

        try:

            import psycopg2
            import os

            from psycopg2 import sql
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE

            con = psycopg2.connect(dbname='postgres',
                user='postgres', host='localhost',
                password=os.environ.get('DB_PASS'))

            con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE

            cur = con.cursor()

            # Use the psycopg2.sql module instead of string concatenation 
            # in order to avoid sql injection attacks.

            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(self.db_name)))

        except Exception as e:

            print_exception(e)

    def create_tables(self, app):

        # make sure its running inside application context or pass one.

        try:

            from root import db

            db.create_all(app=app)

        except Exception as e:
            
            print_exception(e)

    # drop db table

    def drop_table(self, model_class_name, app):

        """

        drop_tbl() >> drop a table from database

        :param1 model_class_name: class name mapped to table (CASE SENSITIVE).
        :param2 app: the application object (app=create_app()) to push app context.

        workflow :

        this function passes <model_class_name> to getattr(<module>, <model_class_name>) to create instance of class
        then drops table using <instance_of_model_class>.__table__.drop(<obj:db_engine>) method
        which takes db engine as argument.

        - import module (models.py module) with importlib.import_module(<string:path.to.module>) method
        - create object of class using getattr(<obj:module>, <string:model_class_name>)
        - create instance of class (cant use anything other than instance of class) by adding
        () to the class object

        return : no return

        """

        try:

            import importlib
            from root import db

            app.app_context().push()

            print('\n')
            print(f'DROPPING TABLE <{ model_class_name }>')
            print('\n')

            module = importlib.import_module("root.database.models")
            class_ = getattr(module, model_class_name)
            instance = class_()

            instance.__table__.drop(db.engine)

            print(f'TABLE <{ model_class_name }> DROPPED SUCCESSFULLY.')
            print('\n')

        except Exception as e:

            print_exception(e)

# CRUD USER.

class CrudUser:

    def delete_user(username):

        try:

            from root import db
            from root.main.models import User
            
            from flask_login import current_user
            
            if current_user.is_admin:

                user = User.query.filter_by(username=username).first()

                db.session.delete(user)
                db.session.commit()

                print(f'{ user.username } DELETED.')
                return f'{ user.username } DELETED.'

            else:

                print('Unauthorized User.')

        except Exception as e:

            print_exception(e)
            
            return e

    def create_user(self, username, passwd, is_confirmed=False, is_admin=False):

        try:

            from root import bcrypt, db
            from root.main.models import User

            passwd = passwd
            hashed_password = bcrypt.generate_password_hash(
                passwd).decode("utf-8")

            user = User(username=username, password=hashed_password,
                        is_confirmed=is_confirmed, is_admin=is_admin)
            
            db.session.add(user)
            db.session.commit()

            ROLE = 'ADMIN' if user.is_admin else 'USER'

            print(f'CREATED USER >> [ USERNAME={ username }, ROLE={ ROLE }, IS_CONFIRMED={ is_confirmed } ]')
            print('\n')

            all_users = User.query.all()

            print('USERS')
            print('------')

            for user in all_users:

                __role = 'ADMIN' if user.is_admin else 'USER'

                print( f'>> { user.username } [ ROLE ----> {  __role } ]' )
            
            print('\n')

        except Exception as e:

            print_exception(e)

# TAKE INPUT FROM USER.

def take_input(question):

    reply = str(input(question+' y / n : ')).lower().strip()
    
    if reply[0] == 'y':
        
        return True

    else:

        return False

# GENERATE AUTH TOKEN.

def generate_auth_token(exp=None):

    """

    generate_auth_token() >> generates authentication token encoded with same X in POS generate_auth_token()

    :param1[int] exp: token expiry duration.

    return : str[auth token]

    """

    try:

        from root.config import Config

        import datetime
        import jwt

        if exp: # <--- WITH EXPIRY

            token = jwt.encode({'xxx': 'xxx', 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=exp)}, Config.MUTUAL_KEY) 

            return token

            # return jsonify({ -------------------------- DEPRECATED BECAUSE WHEN ACCESSED FROM PYTHON ( FLASK CONTEXT PROCESSOR )
            #     "token": token, ----------------------- IT IS JUST  A RESPONSE CODE AND NOT ACTUAL TOKEN
            #     "expires in ( minutes )": exp
            #     })

        else: # <--- WITHOUT EXPIRY

            token = jwt.encode({'xxx': 'xxx'}, Config.MUTUAL_KEY)

            return token

    except Exception as e:

        print_exception(e)

        return '*** EXCEPTION --> CHECK LOGS FOR DETAILES.'

# REQUIRE AUTH TOKEN TO INTEREACT WITH API ENDPOINTS.

def auth_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        from root.config import Config

        from flask import jsonify, request

        import jwt

        # http://127.0.0.1:5000/endpoint?at=alshfjfjdklsfj89549834ur

        token = request.args.get('at') # at ( auth token )

        if not token:

            return jsonify({'message': 'Token is missing!'}), 403

        try:

            data = jwt.decode(token, Config.MUTUAL_KEY, algorithms=["HS256"])

        except Exception as e:

            print_exception(e)

            return jsonify({'EXCEPTION': 'CHECK LOGS FOR MORE DETAILES.'}), 403

        return f(*args, **kwargs)

    return decorated

# REQUIRE CURRENT USER TO HAVE ADMIN ROLE.

def admin_role_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:

            from flask import abort, redirect, url_for, flash
            from flask_login import current_user

            if not current_user.is_authenticated:

                flash('يرجي تسجيل ألدخول', 'info')
                return redirect(url_for('user.login'))

            elif not current_user.is_admin:

                abort(404) # <---- 404 ( NOT FOUND ) INSTEAD OF 403 ( PERMISSION DENIED ) TO ACHIEVE A SNEAK LVL OF 100.

        except Exception as e:

            print_exception(e)

            abort(404) 

        return f(*args, **kwargs)

    return decorated


# GENERATE UNIQUE STRING.

def uuid_url64():

    import re
    import uuid
    import base64

    rv = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
    return re.sub(r'[\=\+\/]', lambda m: {'+': '-', '/': '_', '=': ''}[m.group(0)], rv)

# CONVERT UTC TO LOCAL TIME (UTC+2).

def localTime():

    import pytz
    import datetime

    tz = pytz.timezone('Africa/Cairo')
    utc = datetime.datetime.utcnow()
    local = pytz.utc.localize(utc, is_dst=None).astimezone(tz)

    return local

# SEND CONFIRMATION LINK.

# def send_confirm_email_token(user):

#     from flask_mail import Message
#     from flask import url_for

#     from root import mail

#     token = user.get_reset_token() # <-- CHECK

#     msg = Message('Confirm E-mail',
#                   sender='noreply',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
#                 {url_for('users.reset_token', token=token, _external=True)}
#                 If you did not make this request then simply ignore this email and no changes will be made.
#                 '''
#     mail.send(msg)
