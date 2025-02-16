import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour

    MERCHANDISE = {
        't-shirt': 80,
        'cup': 20,
        'book': 50,
        'pen': 10,
        'powerbank': 200,
        'hoody': 300,
        'umbrella': 200,
        'socks': 10,
        'wallet': 50,
        'pink-hoody': 500
    }

    INITIAL_COINS = 1000