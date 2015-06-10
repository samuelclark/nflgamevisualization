from flask import Flask
import flask.ext.assets as flask_asset
from . import settings
from . import assets_control

app = Flask(__name__)
from . import views
# app settings
assets_control.register_static_resources(app)
