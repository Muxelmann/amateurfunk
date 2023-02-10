import os

development = os.environ.get('FLASK_DEVELOPMENT', 'False') == 'True'
if development:
    from app import create_app
else:
    from .app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(host=host, port=port, debug=debug)