import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql://root:2371@localhost/railway'  # Modify with your database credentials
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Secret key for JWTs and Flask sessions
    SECRET_KEY = os.getenv('999888777666', 'your-default-fallback-key')
