from flask import Blueprint

bp = Blueprint('_util', __name__)

# db must come before grant
from . import db, tmpl, grant, cache
