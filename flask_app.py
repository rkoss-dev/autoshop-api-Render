from app import create_app
from app.extensions import db
from config import ProductionConfig

app = create_app(ProductionConfig)

with app.app_context():
    db.create_all()
