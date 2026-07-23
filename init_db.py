from app import create_app
from app.database import db
import app.models  # Registers models with SQLAlchemy

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("\n SUCCESS! Connected to MySQL and created all database tables!\n")
    except Exception as e:
        print(f"\n❌ Error creating database tables: {e}\n")