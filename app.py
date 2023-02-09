from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from web import login, logout, admin_panel, admin_profile, add_student, edit_user, add_lecturer, edit_lecturer, \
    add_appointment, set_appointment, lecturer_panel, edit_appointment, add_record, edit_record, student_profile, \
    lecturer_profile, \
    del_appointment, send_msg, add_category, search, edit_category

# Configuration do not touch
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'  # important to change in production !!!!
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


app.config.update(
    SESSION_COOKIE_SECURE=False,  # change it to True when ssl is on
    SESSION_COOKIE_HTTPONLY=False,  # change to True when ssl is on
    SESSION_COOKIE_SAMESITE='Lax',

)
csrf = CSRFProtect(app)
login_manager.refresh_view = "login.login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"
# app.config.update(WTF_CSRF_CHECK_DEFAULT=False)
defualt_content_policy = "default-src 'self'; img-src 'self' data: "
js_content_policy = " script-src 'self' 'unsafe-inline' "
css_content_policy = " style-src https: 'self' 'unsafe-inline' "


#todo add tables for categories and edit category

# _____________Dictionary________
# appo is the abbreviated of appointment
# lect is abbreviated of lecterur
# rec is abbreviated of record



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# create the tabeles
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    uname = db.Column(db.String(100), unique=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=None)
    tags = db.Column(db.Text)
    desc = db.Column(db.Text)
    image = db.Column(db.Text)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    category = db.Column(db.String(100), nullable=False, unique=True)
    sub_category = db.Column(db.Text)


class Appointment(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    uname = db.Column(db.String(100))
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    appo_date = db.Column(db.String(100))
    appo_start_hour = db.Column(db.String(10))
    appo_end_hour = db.Column(db.String(10))
    appo_dur = db.Column(db.String(5))
    appo_loc = db.Column(db.String(100))
    appo_type = db.Column(db.String(100))
    appo_limit = db.Column(db.Integer)
    appo_user_aproved = db.Column(db.Text)
    appo_user_wait = db.Column(db.Text)
    appo_msg = db.Column(db.Text)


class Record(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    category = db.Column(db.String(100))
    title = db.Column(db.String(100))
    link = db.Column(db.String(100), unique=True)
    desc = db.Column(db.Text)
    tags = db.Column(db.Text)


# ------------ to create the tables ------------
# with app.app_context():
#     db.create_all()
#     admin = User(uname="admin",fname="admin",lname="admin",password=generate_password_hash("SyZueCyg)MJUw@9=",method='pbkdf2:sha256',salt_length=8),role="admin",category="aaa")
#     db.session.add(admin)
#     db.session.commit()
#     db.session.commit()

if __name__ == '__main__':
    app.register_blueprint(login.login_bp)
    app.register_blueprint(logout.logout_bp)
    app.register_blueprint(admin_panel.admin_panel_bp)
    app.register_blueprint(admin_profile.admin_profile_bp)
    app.register_blueprint(add_student.add_student_bp)
    app.register_blueprint(edit_user.edit_user_bp)
    app.register_blueprint(add_lecturer.add_lecturer_bp)
    app.register_blueprint(edit_lecturer.edit_lecturer_bp)
    app.register_blueprint(add_appointment.add_appointment_bp)
    app.register_blueprint(set_appointment.set_appointment_bp)
    app.register_blueprint(lecturer_panel.lecturer_panel_bp)
    app.register_blueprint(edit_appointment.edit_appointment_bp)
    app.register_blueprint(add_record.add_record_bp)
    app.register_blueprint(edit_record.edit_record_bp)
    app.register_blueprint(student_profile.student_profile_bp)
    app.register_blueprint(lecturer_profile.lecturer_profile_bp)
    app.register_blueprint(del_appointment.del_appointment_bp)
    app.register_blueprint(send_msg.send_msg_bp)
    app.register_blueprint(add_category.add_category_bp)
    app.register_blueprint(search.search_bp)
    app.register_blueprint(edit_category.edit_category_bp)
    app.run(host="0.0.0.0")
