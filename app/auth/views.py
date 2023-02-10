from flask import Flask, Blueprint, session, redirect, url_for, request, g, render_template

class AuthView:
    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        bp = Blueprint('auth', __name__, url_prefix='/auth')

        @bp.before_app_request
        def load_registered_user():
            g.registered_user_id = session.get('user-id', None)

        @bp.route('/')
        def index():
            return render_template('auth/register.jinja2')

        @bp.route('/register', methods=['POST'])
        def register():
            user_id = request.form.get('user-id', None)
            if user_id is not None:
                session.clear()
                session['user-id'] = user_id
                
            return redirect(url_for('index'))

        @bp.route('/logout')
        def logout():
            session.clear()
            return redirect(url_for('index'))

        app.register_blueprint(bp)