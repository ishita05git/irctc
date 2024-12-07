from app import app
from models import db

# Create all the tables
with app.app_context():
    db.create_all()
