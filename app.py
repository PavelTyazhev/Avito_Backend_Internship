from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy()
jwt = JWTManager()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'sslmode': 'require'
            }
        }

    db.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from routes import api, auth, shop
    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(shop)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

@login_manager.user_loader
def load_user(id):
    from models import User
    return User.query.get(int(id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)