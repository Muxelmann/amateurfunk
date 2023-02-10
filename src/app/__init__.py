from flask import Flask, render_template
import json
import os
import random

from .question import QuestionView
from .auth import AuthView, registration_required

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('FLASK_SECRET') or os.urandom(16)

    if not os.path.exists(app.instance_path):
        os.mkdir(app.instance_path)

    AuthView(app)
    QuestionView(app)

    @app.route('/')
    @registration_required
    def index():
        return render_template('index.jinja2')

    return app