import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'car-sos-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'car_sos.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PLIVO_AUTH_ID = os.environ.get('PLIVO_AUTH_ID', '')
    PLIVO_AUTH_TOKEN = os.environ.get('PLIVO_AUTH_TOKEN', '')
    PLIVO_PHONE_NUMBER = os.environ.get('PLIVO_PHONE_NUMBER', '')
    SITE_URL = os.environ.get('SITE_URL') or 'https://digitaldreamer.in'

    # Owner-first SOS escalation
    OWNER_CALL_TIMEOUT_SECONDS = int(os.environ.get('OWNER_CALL_TIMEOUT_SECONDS', 30))
    SOS_COOLDOWN_MINUTES = int(os.environ.get('SOS_COOLDOWN_MINUTES', 5))
