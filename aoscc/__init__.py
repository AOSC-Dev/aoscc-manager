import os
import sys
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request

from .config import *
from .secret import SECRET
from .util import bp as util_bp
from .user import bp as user_bp
from .admin import bp as admin_bp
from .util.tg import bot_main


def make_app() -> Flask:
    app = Flask(__name__)
    app.config.update({
        'SECRET_KEY': SECRET,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'SESSION_COOKIE_SECURE': True,
        'PERMANENT_SESSION_LIFETIME': SESSION_EXPIRY,
        'MAX_CONTENT_LENGTH': MAX_FILE_SIZE,
        'TEMPLATES_AUTO_RELOAD': True,
    })
    if TESTING:
        app.config.update({
            'SESSION_COOKIE_SECURE': False,
        })

    os.makedirs(app.instance_path, exist_ok=True)
    os.chdir(app.instance_path)

    db = sqlite3.connect(Path(app.instance_path) / 'aoscc.sqlite')
    with app.open_resource('schema.sql', 'r') as sql:
        db.executescript(sql.read())
    db.close()

    app.register_blueprint(util_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.get("/robots.txt")
    def robots():
        return "User-agent: *\nDisallow: /"

    @app.get('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.before_request
    def fix_remote_addr():
        request.remote_addr = request.headers.get('X-Real-IP', request.remote_addr)

    return app


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'tgbot':
        bot_main()
    else:
        make_app().run(debug=True)
