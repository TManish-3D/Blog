from functools import wraps
from flask_login import current_user
from flask import flash ,redirect,url_for

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("You must be an admin to access this page.", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

"""from werkzeug.security import generate_password_hash

admin = User(
    username="admin",
    email="admin@blog.com",
    password=generate_password_hash("StrongPassword123"),
    role="admin"
)

db.session.add(admin)
db.session.commit()"""