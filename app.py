from app import create_app, db
import os

app = create_app()
app.secret_key = os.environ.get("SECRET_KEY", "change_this_dev_key")

with app.app_context():
    # Automatically creates tables if they don’t exist
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
