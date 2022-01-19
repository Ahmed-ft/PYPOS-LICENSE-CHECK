# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, login_user, current_user, logout_user

from root import create_app, db, bcrypt
from root.main.utils import uuid_url64, generate_auth_token, auth_token_required, create_user
from root.main.models import DeviceReg, LicenseKey, User

main = Blueprint("main", __name__, template_folder="templates")

# REMOVE WHEN DONE
# REMOVE WHEN DONE
# REMOVE WHEN DONE

@main.route('/t')
def __get_token():

    t = generate_auth_token()

    return t

@main.route('/reset')
def reset_db():

    try:

        app = create_app()

        db.create_all(app=app)

    except Exception as e:

        print(e)

    return 'db reset done'

@main.route('/su')
def create_admin():

    try:

        create_user('admin', '0000')

    except Exception as e:

        print(e)

    return 'admin created successfully'

@main.route('/generate_keys')
def generate_keys():

    keys = LicenseKey.query.first()

    if keys:

        return 'KEYS EXISTS.'

    counter = 1

    while counter < 100:

        unique_key = uuid_url64()
        new_license_key = LicenseKey(key=unique_key)

        db.session.add(new_license_key)
        db.session.commit()

        counter+=1

    print('GENERATING LICENSE KEYS >> DONE')
    return 'GENERATING LICENSE KEYS >> DONE'

# REMOVE WHEN DONE
# REMOVE WHEN DONE
# REMOVE WHEN DONE

@main.route('/')
@login_required
def index():

    return render_template('/main/index.html')

@main.route('/logout')
def logout():

    logout_user()

    return 'LOGGED OUT.'

@main.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:

        return f'{current_user.username} IS ALREADY LOGGED IN.'

    if request.method == 'POST':

        user = User.query.filter_by(username=request.form['username']).first()

        if user is None:

            return 'USER DOES NOT EXIST'

        elif not bcrypt.check_password_hash(user.password, request.form['password']):

            return 'CHECK YOUR PASSWORD'

        elif user and bcrypt.check_password_hash(user.password, request.form['password']):

            login_user(user)

            return redirect(url_for('main.index'))

    return render_template('/main/login.html')

@main.route('/list_keys')
@login_required
def list_keys():

    keys = LicenseKey.query.all()

    return render_template("/main/list_keys.html", keys=keys)

@main.route('/list_regs')
@login_required
def list_regs():

    regs = DeviceReg.query.all()

    return render_template("/main/list_regs.html", regs=regs)

# verify license for device (TOKEN REQUIRED)

@main.route('/api/verify_license', methods=['POST'])
@auth_token_required
def verify_license():

    # SYS INFO

    device_uuid = request.json['device_uuid']
    device_serial_number = request.json['device_serial_number']
    device_baseboard_serial = request.json['device_baseboard_serial']
    license_key = request.json['license_key']

    # CHECK IF LICENSE IS VALID

    print('VALIDATING LICESNSE...')

    valid_license = LicenseKey.query.filter_by(key=license_key).first()

    if valid_license: # <-------- [ LICENSE IS VALID ]

        # CHECK IF DEVICE IS REGISTERED.

        print('LICENSE IS VALID. CHECKING IF THE DEVICE IS REGISTERED.')

        is_registered_device = DeviceReg.query.filter_by(uuid=device_uuid).first()

        if is_registered_device: # <-------- [ ALREADY REGISTERED ] [ R-1 ]

            print('ALREADY REGISTERED.')
            return 'R-1'

        else: # <-------- [ NOT REGISTERED ]

            # CHECK IF LICENSE IS USED BY ANOTHER DEVICE.

            print('CHECKING IF LICENSE IS USED...')

            if valid_license.status == 'USED': # <-------- [ USED LICENSE ] [ R-2 ]

                print('USED LICENSE.')
                return 'R-2'

            else: # LICENSE STATUS == NEW

                print('LICENSE IS VALID. REGISTERING DEVICE...')

                new_device_reg = DeviceReg(uuid=device_uuid, serial_number=device_serial_number, baseboard_serial_number=device_baseboard_serial,
                license_key=license_key)

                valid_license.status = 'USED'
                
                db.session.add(new_device_reg)
                db.session.commit()

                print('DEVICE REGISTERED SUCCESSFULLY.')
                return 'R-3' # <-------- [ DEVICE REGISTERED SUCCESSFULLY ] [ R-3 ]

    else:
        
        print('LICENSE NOT VALID.')
        return 'R-4' # <-------- [ LICENSE NOT VALID ] [ R-4 ]