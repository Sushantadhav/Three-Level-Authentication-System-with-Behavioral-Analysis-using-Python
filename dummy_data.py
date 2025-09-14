# app/dummy_data.py

import random
from datetime import datetime, timedelta
from faker import Faker
from app import db
from app.models import User, BehaviorLog

fake = Faker()

def insert_dummy_data():
    print("Inserting dummy data into SQLite...")

    # Pehle sab clear kar dete hai (optional)
    BehaviorLog.query.delete()
    User.query.delete()
    db.session.commit()

    users = []
    logs = []

    for i in range(500):
        # Random user banate hain
        user = User(
            username=fake.user_name() + str(random.randint(100, 999)),
            password="hashed_password_here",  # tum apna password hash dal sakte ho
            click_x=random.randint(0, 500),
            click_y=random.randint(0, 500),
            image_filename="auth_image.jpg",
            secret_color=random.choice(["red", "green", "blue"]),
            color_sequence=random.choice(["RGB", "BGR", "GRB", "BRG"]),
            level2_passed=random.choice([True, False]),
            is_admin=False,
            created_at=fake.date_time_between(start_date="-1y", end_date="now")
        )
        users.append(user)
        db.session.add(user)

    db.session.commit()

    # Ab behavior logs insert karte hain
    for user in users:
        for _ in range(random.randint(3, 10)):  # har user ke 3-10 logs
            log = BehaviorLog(
                user_id=user.id,
                action=random.choice(["login_attempt", "image_click", "color_select"]),
                data=fake.sentence(),
                ip_address=fake.ipv4(),
                timestamp=fake.date_time_between(start_date="-1y", end_date="now")
            )
            logs.append(log)
            db.session.add(log)

    db.session.commit()
    print("Dummy data inserted successfully!")

if __name__ == "__main__":
    from run import app  # tumhare Flask app ka entry point

    with app.app_context():
        db.create_all()  # agar table nahi hai to bana dega
        insert_dummy_data()
