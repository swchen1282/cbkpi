import os

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.getenv('TMPDIR', '/tmp')


class Config(object):
    # APP
    APP_NAME = 'cathay_api'
    APP_VER = '1.0'
    APP_DESC = 'maintained by swchen'
