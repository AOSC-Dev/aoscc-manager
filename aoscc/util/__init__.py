from flask import Blueprint

bp = Blueprint('_util', __name__)

from . import db, tmpl, grant
