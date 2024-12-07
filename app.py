from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import routes

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database and JWT manager
db.init_app(app)
jwt = JWTManager(app)

# Register routes blueprint
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)
