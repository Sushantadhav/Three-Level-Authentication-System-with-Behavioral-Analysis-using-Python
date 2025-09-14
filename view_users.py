from app import create_app, db
from app.models import User, BehaviorLog

app = create_app()
with app.app_context():
    print("Users Table:")
    for u in User.query.all():
        print(u.id, u.username, u.image_filename, u.color_sequence, u.created_at)

    print("\nBehavior Logs:")
    for log in BehaviorLog.query.all():
        print(log.id, log.user_id, log.action, log.data, log.timestamp)
