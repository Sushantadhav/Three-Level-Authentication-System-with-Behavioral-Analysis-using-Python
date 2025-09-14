# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, render_template_string
from app.auth_utils import hash_password, check_password
from app import  db
from app.models import User, BehaviorLog
from datetime import datetime
import json, csv, os, sqlite3
from io import StringIO
import pandas as pd
import random
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required.", "danger")
            return redirect(url_for("auth.login"))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash("❌ You are not authorized to view this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# ========== Helper function for logging ==========
def log_behavior(user_id, action, data=None):
    ip = request.remote_addr
    entry = BehaviorLog(user_id=user_id, action=action, data=json.dumps(data or {}), ip_address=ip)
    db.session.add(entry)
    db.session.commit()

# ========== Routes ==========
@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

# ---------- Login ----------
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password(password, user.password):
            flash("Login successful!", "success")
            session['user_id'] = user.id
            session['level1_passed'] = True
            session['level2_passed'] = False
            session['level3_passed'] = False
            log_behavior(user.id, "login_success", {"username": username})
            return redirect(url_for('auth.image_click_auth'))
        else:
            if user:
                log_behavior(user.id, "login_failed", {"username": username})
            flash("Invalid username or password.", "danger")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

# ---------- Register ----------
@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        click_x = request.form.get('click_x')
        click_y = request.form.get('click_y')
        color_sequence = request.form.get('color_sequence')
        image_filename = 'auth_image.jpg'

        if not username or not password:
            flash("Username and Password are required.", "danger")
            return render_template("register.html")

        if not click_x or not click_y:
            flash("Please click on the image for Level 2.", "danger")
            return render_template("register.html")

        if not color_sequence or len(color_sequence) != 3:
            flash("Please select a valid 3-color sequence.", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return render_template("register.html")

        hashed = hash_password(password)
        new_user = User(
            username=username,
            password=hashed,
            click_x=int(click_x),
            click_y=int(click_y),
            image_filename=image_filename,
            color_sequence=color_sequence
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template("register.html")

# ---------- Level 2 Authentication ----------
@auth_bp.route('/level2_image', methods=['GET','POST'])
def image_click_auth():
    if 'user_id' not in session:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        click_x = request.form.get('click_x')
        click_y = request.form.get('click_y')
        if not click_x or not click_y:
            flash("Please click on the image before submitting.", "danger")
            return redirect(url_for('auth.image_click_auth'))

        click_x = int(click_x); click_y = int(click_y)
        margin = 20
        if abs(click_x - (user.click_x or 0)) <= margin and abs(click_y - (user.click_y or 0)) <= margin:
            user.level2_passed = True
            db.session.commit()
            session['level2_passed'] = True
            log_behavior(user.id, "image_click_match", {"clicked_x": click_x, "clicked_y": click_y})
            return redirect(url_for('auth.level3_rgb'))
        else:
            log_behavior(user.id, "image_click_fail", {"clicked_x": click_x, "clicked_y": click_y})
            flash("❌ Incorrect click location. Try again.", "danger")
            return redirect(url_for('auth.image_click_auth'))

    return render_template('level2_image.html', image_filename=user.image_filename or 'auth_image.jpg')

# ---------- Level 3 Authentication ----------
@auth_bp.route('/level3_rgb', methods=['GET','POST'])
def level3_rgb():
    if 'user_id' not in session:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('auth.login'))

    if not session.get('level2_passed'):
        flash("Please complete image click authentication first.", "warning")
        return redirect(url_for('auth.image_click_auth'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        submitted = request.form.get('color_sequence', '')
        if not submitted:
            flash("Please select a color sequence.", "danger")
            return redirect(url_for('auth.level3_rgb'))

        if submitted == user.color_sequence:
            log_behavior(user.id, "color_sequence_match", {"submitted": submitted})
            flash("✅ Level 3 Authentication successful!", "success")
            session['login_time'] = str(datetime.now())
            session['level3_passed'] = True  # 🔑 Needed for dashboard access

            if user.is_admin:
                return redirect(url_for('auth.dashboard'))  # ✅ Redirect instead of render
            else:
                flash(f"✅ Thanks for logging in, {user.username}", "info")
                return redirect(url_for('auth.user_home'))

        else:
            log_behavior(user.id, "color_sequence_fail", {"submitted": submitted})
            flash("❌ Incorrect color sequence. Try again.", "danger")
            return redirect(url_for('auth.level3_rgb'))

    return render_template("level3_rgb.html")

@auth_bp.route('/user_home')
@login_required
def user_home():
    if 'user_id' not in session:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.login'))

    return render_template("user_home.html", user=user)

@auth_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # 1️⃣ Check login + Level 3
    if 'user_id' not in session or not session.get('level3_passed'):
        flash("❌ Complete 3-level authentication to access dashboard.", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("❌ User not found!", "danger")
        return redirect(url_for('auth.login'))

    login_time = session.get('login_time', "Not recorded")

    if user.is_admin:
        # ✅ Admin ke liye dashboard render karo
        return render_template("dashboard.html", user=user, login_time=login_time)
    else:
        # 👤 Normal users ke liye sirf message
        flash(f"✅ Thanks for logging in, {user.username}! Dashboard is only for admins.", "info")
        return redirect(url_for('auth.user_home'))  # ya koi normal user home page

# ---------- Admin: Logs ----------
@auth_bp.route('/admin/logs', methods=["GET", "POST"])
@admin_required
def view_logs():
    # Pehle login check
    if 'user_id' not in session:
        flash("Login required to view logs.", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash("❌ You are not authorized to view this page.", "danger")
        return redirect(url_for('auth.login'))

    # # ---- Password Protection ----
    # SECRET_PASS = "Logs@123"   # <-- yaha apna strong password daalo
    # if request.method == "POST":
    #     if request.form.get("pass") != SECRET_PASS:
    #         return "❌ Wrong password", 403
    # else:
    #     # Pehli baar open hua to form dikhao
    #     return render_template_string("""
    #         <form method="post">
    #             <h3>Enter password to view Logs</h3>
    #             <input type="password" name="pass" required>
    #             <button type="submit">Submit</button>
    #         </form>
    #     """)

    # ---- Agar password sahi hai to logs dikhao ----
    logs = db.session.query(BehaviorLog, User).join(User).order_by(BehaviorLog.timestamp.desc()).all()
    processed = [{
        'id': log.id,
        'username': u.username,
        'action': log.action,
        'data': log.data,
        'ip_address': log.ip_address,
        'timestamp': log.timestamp
    } for log, u in logs]

    return render_template("logs.html", logs=processed)

# ---------- Admin: Logs Download ----------
@auth_bp.route('/admin/logs/download')
@admin_required
def download_logs_csv():
    logs = db.session.query(BehaviorLog, User).join(User).order_by(BehaviorLog.timestamp.desc()).all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Username", "Action", "Data", "IP Address", "Timestamp"])
    for log, u in logs:
        writer.writerow([log.id, u.username, log.action, log.data, log.ip_address, log.timestamp])
    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=behavior_logs.csv"})

@auth_bp.route("/admin/users")
@admin_required
def view_users():
    if 'user_id' not in session:
        flash("Login required.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash("❌ You are not authorized to view this page.", "danger")
        return redirect(url_for("auth.login"))

    users = User.query.all()
    return render_template("view.html", users=users)

# ---------- Behavior Report (Password Protected) ----------
@auth_bp.route("/behavior-report", methods=["GET", "POST"])
@admin_required
def behavior_report():
    # SECRET_PASS = "Abcd"
    # if request.method == "POST":
    #     if request.form.get("pass") != SECRET_PASS:
    #         return "❌ Wrong password", 403
    # else:
    #     return render_template_string("""
    #         <form method="post" class="p-4">
    #             <h3>Enter password to view report</h3>
    #             <input type="password" name="pass" required>
    #             <button type="submit" class="btn btn-primary">Submit</button>
    #         </form>
    #     """)

    # Login stats
    success_count = BehaviorLog.query.filter_by(action="login_success").count()
    fail_count = BehaviorLog.query.filter(BehaviorLog.action.like("login_fail%")).count()

    # Image click stats
    img_success = BehaviorLog.query.filter_by(action="image_click_match").count()
    img_fail = BehaviorLog.query.filter_by(action="image_click_fail").count()

    # Color sequence stats
    color_success = BehaviorLog.query.filter_by(action="color_sequence_match").count()
    color_fail = BehaviorLog.query.filter_by(action="color_sequence_fail").count()

    # Top IPs
    top_ips = db.session.query(
        BehaviorLog.ip_address, db.func.count(BehaviorLog.id)
    ).group_by(BehaviorLog.ip_address).order_by(db.func.count(BehaviorLog.id).desc()).limit(10).all()

    # Suspicious IPs (>5 fails)
    suspicious_ips = db.session.query(
        BehaviorLog.ip_address, db.func.count(BehaviorLog.id)
    ).filter(BehaviorLog.action.like("login_fail%")) \
     .group_by(BehaviorLog.ip_address) \
     .having(db.func.count(BehaviorLog.id) > 5).all()

    # 🔥 Top active users (most logins)
    top_users = db.session.query(
        User.username, db.func.count(BehaviorLog.id)
    ).join(BehaviorLog).filter(BehaviorLog.action == "login_success") \
     .group_by(User.username).order_by(db.func.count(BehaviorLog.id).desc()).limit(5).all()

    # 🔥 Users with most failed attempts
    failed_users = db.session.query(
        User.username, db.func.count(BehaviorLog.id)
    ).join(BehaviorLog).filter(BehaviorLog.action.like("login_fail%")) \
     .group_by(User.username).order_by(db.func.count(BehaviorLog.id).desc()).limit(5).all()

    # 🔥 Daily login trend (success/fail per date)
    daily_stats = db.session.query(
        db.func.date(BehaviorLog.timestamp),
        db.func.sum(db.case((BehaviorLog.action=="login_success", 1), else_=0)),
        db.func.sum(db.case((BehaviorLog.action.like("login_fail%"), 1), else_=0))
    ).group_by(db.func.date(BehaviorLog.timestamp)).all()

    # Format daily stats for chart.js
    dates = [str(d[0]) for d in daily_stats]
    success_trend = [d[1] for d in daily_stats]
    fail_trend = [d[2] for d in daily_stats]

    return render_template(
        "behavior_report.html",
        success_count=success_count,
        fail_count=fail_count,
        img_success=img_success,
        img_fail=img_fail,
        color_success=color_success,
        color_fail=color_fail,
        top_ips=top_ips,
        suspicious_ips=suspicious_ips,
        top_users=top_users,
        failed_users=failed_users,
        dates=dates,
        success_trend=success_trend,
        fail_trend=fail_trend,
        avg_duration=0
    )
# ---------- Dummy Data Generator (for testing only) ----------




    db_path = os.path.join(os.path.dirname(__file__), "..", "database.db")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT b.id, u.username, b.action, b.data, b.ip_address, b.timestamp
        FROM behavior_logs b
        JOIN users u ON b.user_id = u.id
    """, conn)
    conn.close()

    total_actions = len(df)
    action_counts = df['action'].value_counts().to_dict()
    suspicious_users = df[df['action'] == 'login_failed']['username'].value_counts().to_dict()

    return render_template("behavior_report.html",
                           total_actions=total_actions,
                           action_counts=action_counts,
                           suspicious_users=suspicious_users)

# ---------- Delete all non-admin users + their logs ----------
@auth_bp.route("/clear-nonadmin")
def clear_nonadmin():
# saare non-admin users nikal lo
    non_admins = User.query.filter_by(is_admin=False).all()
    for u in non_admins:
# unke saare logs delete ho jayenge cascade se
        db.session.delete(u)

    db.session.commit()
    return "✅ Non-admin users aur unke logs delete ho gaye!"