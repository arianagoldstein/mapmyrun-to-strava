from flask import Flask
import secrets

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    # Import and register the blueprint from routes.py
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app