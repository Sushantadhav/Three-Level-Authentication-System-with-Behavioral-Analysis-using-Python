from app import create_app, db
import os

app = create_app()
app.secret_key = os.urandom(24)
# Auto-create database if not exists
with app.app_context():
    if not os.path.exists(os.path.join(app.instance_path, 'database.db')):
        print("Database file not found, creating...")
        db.create_all()
        print("Database created successfully!")
    else:
        print("Database already exists.")

if __name__ == '__main__':
    app.run(debug=True)
