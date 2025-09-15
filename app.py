from app import create_app, db
import os

app = create_app()

app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

with app.app_context():
    database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")
    if database_url.startswith("sqlite"):
        db_path = database_url.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            print("Database file not found, creating...")
            db.create_all()
            print("Database created successfully!")
        else:
            print("Database already exists.")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
