from root import db, login_manager
from root.main.utils import localTime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    __tabelname__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(100))
    
    timestamp = db.Column(db.DateTime, nullable=False, default=localTime())

    def get_reset_token(self, expires_sec=1800):

        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):

        s = Serializer(current_app.config['SECRET_KEY'])

        try:
        
            user_id = s.loads(token)['user_id']
        
        except:
        
            return None
        
        return User.query.get(user_id)

class LicenseKey(db.Model):
   
    __tabelname__ = 'license_key'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True)
    status = db.Column(db.String, default='NEW')
    timestamp = db.Column(db.DateTime, nullable=False, default=localTime())


class DeviceReg(db.Model):
   
    __tabelname__ = 'device_reg'
   
    id = db.Column(db.Integer, primary_key=True)
    business_type = db.Column(db.String)
    uuid = db.Column(db.String, unique=True)
    serial_number = db.Column(db.String, unique=True)
    baseboard_serial_number = db.Column(db.String, unique=True)
    license_key = db.Column(db.String)
    timestamp = db.Column(db.DateTime, nullable=False, default=localTime())