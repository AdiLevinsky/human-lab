from flask import Flask, render_template, redirect, url_for, flash, abort, request, make_response
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user, \
    fresh_login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
import calendar
from forms import LoginForm, add_studnet, add_Lecturer, add_Appointment, add_record, add_category
import functions, re
import htmlentities
from flask_wtf.csrf import CSRFProtect
import os

# Configuration do not touch
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',

)
csrf = CSRFProtect(app)
login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"
# app.config.update(WTF_CSRF_CHECK_DEFAULT=False)
defualt_content_policy = "default-src 'self'; img-src 'self' data: "
js_content_policy = " script-src 'unsafe-inline'  http://127.0.0.1:5000/static/vendor/jquery/jquery-3.6.0.min.js http://127.0.0.1:5000/static/vendor/bootstrap-5.1.3-dist/js/bootstrap.bundle.min.js "
css_content_policy = " style-src https: 'unsafe-inline'  http://127.0.0.1:5000/static/vendor/bootstrap-5.1.3-dist/css/bootstrap.min.css "


# todo אפשרות חיפוש זה אופצינאלי
# todo להוסיף את ההערות בטבלה של האדמין

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



# with app.app_context():
#     db.create_all()
    # admin = User(uname="admin",fname="admin",lname="admin",password=generate_password_hash("SyZueCyg)MJUw@9=",method='pbkdf2:sha256',salt_length=8),role="admin",category="aaa")
    # db.session.add(admin)
    # db.session.commit()
    # db.session.commit()

@app.route('/', methods=["POST", "GET"])
def login():  # put application's code here
    # for auto delete of old appoitmnets
    appo_user = Appointment.query.order_by(Appointment.appo_date,
                                           Appointment.appo_start_hour).all()
    for i in range(len(appo_user)):
        if appo_user[i].appo_date < datetime.datetime.now().strftime("%Y-%m-%d") or appo_user[i].appo_date \
                == datetime.datetime.now().strftime("%Y-%m-%d") \
                and appo_user[i].appo_start_hour < datetime.datetime.now().strftime("%H:%M"):
            Appointment.query.filter_by(id=appo_user[i].id).delete()
            db.session.commit()

    if not current_user.is_authenticated:  # if the user isn't log in
        form = LoginForm()  # call the login form from forms.py
        if form.validate_on_submit():
            uname = htmlentities.encode(form.uname.data)  # prevent xss
            password = htmlentities.encode(form.password.data)  # prevent xss

            user = User.query.filter_by(uname=uname).first()
            # Email doesn't exist or password incorrect.
            if not user:
                flash("משתמש לא קיים")
                return redirect(url_for('login'))
            elif not check_password_hash(user.password, password):
                flash('סיסמה לא נכונה נסה שוב')
                return redirect(url_for('login'))
            else:
                # redrect by role
                login_user(user)
                if current_user.role == "admin":
                    return redirect(url_for('admin_panel'))
                if current_user.role == "lecturer":
                    return redirect(url_for("lecturer_panel"))
                return redirect(url_for("set_appo"))
        response = make_response(render_template("index.html", form=form))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/index.css;"
        return response
    else:  # if the use log in
        if current_user.role == "admin":
            return redirect(url_for('admin_panel'))
        if current_user.role == "lecturer":
            return redirect(url_for("lecturer_panel"))
        return redirect(url_for("set_appo"))


@app.route('/adminPanel', methods=["GET", "POST"])
@fresh_login_required
def admin_panel():
    if current_user.id == 1:
        if request.method == "POST":
            # show the table choosen by the admin
            try:
                choose = htmlentities.encode(request.form["choose"])
            except:
                choose = ""
            if choose == "users":
                student_tb = User.query.filter_by(role="student").all()  # get all students
                table_len = range(len(student_tb))  # table len is for the for loop in the html
                response = make_response(render_template("adminPanel.html", table_len=table_len, st_table=student_tb,
                                                         current_user=current_user, choose=choose))
                response.headers['Content-Security-Policy'] = defualt_content_policy + \
                                                              ";" + js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + \
                                                              css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
            elif choose == "lecturers":
                student_tb = User.query.filter_by(role="lecturer").all()  # get all lecterurs
                table_len = range(len(student_tb))  # table len is for the for loop in the html
                response = make_response(render_template("adminPanel.html", table_len=table_len, st_table=student_tb,
                                                         current_user=current_user, choose=choose))
                response.headers['Content-Security-Policy'] = defualt_content_policy + \
                                                              ";" + js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + \
                                                              css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response

            elif choose == "appos":
                if "search1" in request.form:
                    appo_user = Appointment.query.filter_by(uname=request.form["search1"]).order_by(
                        Appointment.appo_date,
                        Appointment.appo_start_hour).all()
                else:
                    appo_user = Appointment.query.order_by(Appointment.appo_date,
                                                           Appointment.appo_start_hour).all()  # get all users appointments

                table_len = range(len(appo_user))  # table len is the length of the table
                for i in table_len:
                    if appo_user[i].appo_user_wait:  # if it's not none
                        temp = appo_user[i].appo_user_wait.replace("\n", "")
                        if temp:
                            appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.split("\n")[
                                                          1:]  # the users in appo_user_wait save \n name...\n name \n ..... so get list of all users I split by \n
                            appo_user[i].appo_user_wait.append(len(appo_user[
                                                                       i].appo_user_wait))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                        else:
                            appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.replace("\n",
                                                                                              "")  # else if no user wait for approve the objects value become to "" which is nothing
                    if appo_user[i].appo_user_aproved:  # if it's not none
                        temp = appo_user[i].appo_user_aproved.replace("\n", "")
                        if temp:
                            appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.split("\n")[
                                                             1:]  # the users in appo_user_aproved save \n name...\n name \n ..... so get list of all users I split by \n
                            appo_user[i].appo_user_aproved.append(len(appo_user[
                                                                          i].appo_user_aproved))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                        else:
                            appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.replace("\n",
                                                                                                    "")  # else if no user wait for approve the objects value become to "" which is nothing
                response = make_response(
                    render_template("adminPanel.html", table_len=table_len, appo_user=appo_user, choose="appos"))
                response.headers['Content-Security-Policy'] = defualt_content_policy + \
                                                              ";" + \
                                                              js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + \
                                                              css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
            elif choose == "records":
                records_tb = Record.query.all()  # get all records
                table_len = range(len(records_tb))  # the length of records table
                response = make_response(
                    render_template("adminPanel.html", table_len=table_len, records_tb=records_tb, choose="records"))
                response.headers['Content-Security-Policy'] = defualt_content_policy + \
                                                              ";" + js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ; " + \
                                                              css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
            if "action" in request.form:  # the action name is for confirmation delete and reject
                if request.form[
                    "action"] == "אישור":  # delete the users from the waiting to approve column in the row of the appoinntment and add the user the approved users for the appointment
                    appo_approve = Appointment.query.filter_by(uname=htmlentities.encode(request.form["lect_name"]),
                                                               appo_date=htmlentities.encode(request.form["ap_date"]),
                                                               appo_start_hour=htmlentities.encode(
                                                                   request.form["ap_hour_st"])).first()
                    if appo_approve.appo_user_aproved:
                        appo_approve.appo_user_aproved = appo_approve.appo_user_aproved + "\n" + htmlentities.encode(
                            request.form["add_user"])  # prevent xss
                        appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace(
                            "\n" + htmlentities.encode(request.form["add_user"]), "")

                    else:
                        appo_approve.appo_user_aproved = "\n" + htmlentities.encode(
                            request.form["add_user"])  # prevent xss
                        appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace(
                            "\n" + htmlentities.encode(request.form["add_user"]), "")  # prevent xss
                    db.session.commit()
                    return redirect(url_for("admin_panel"))
                elif request.form[
                    "action"] == "דחייה":  # delete the users from the waiting to approve column in the row of the appoinntment
                    appo_rej = Appointment.query.filter_by(uname=htmlentities.encode(request.form["lect_name"]),
                                                           appo_date=htmlentities.encode(request.form["ap_date"]),
                                                           appo_start_hour=htmlentities.encode(
                                                               request.form["ap_hour_st"])).first()  # prevent xss
                    appo_rej.appo_user_wait = appo_rej.appo_user_wait.replace("\n" + request.form["add_user"],
                                                                              "")  # prevent xss
                    db.session.commit()
                    return redirect(url_for("admin_panel"))
                elif request.form["action"] == "מחק":  # delete the users from the approved users for the appointment
                    appo_del = Appointment.query.filter_by(uname=request.form["lect_name"],
                                                           appo_date=request.form["ap_date"],
                                                           appo_start_hour=request.form["ap_hour_st"]).first()
                    appo_del.appo_user_aproved = appo_del.appo_user_aproved.replace("\n" + request.form["del_user"], "")
                    if not appo_del.appo_user_aproved:
                        appo_del.appo_user_aproved == ""
                    db.session.commit()
                    return redirect(url_for("admin_panel"))
        if request.method == "GET":
            response = make_response(render_template("adminPanel.html", choose="bb"))  # used for check
            response.headers[
                'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + css_content_policy + "http://127.0.0.1:5000/static/css/adminpanel.css"
            return response

    return abort(403)


@app.route("/logout")
@fresh_login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/add studet', methods=["GET", "POST"])
@fresh_login_required
def add_student():
    if current_user.id == 1:
        form = add_studnet()  # call the add student form from forms.py
        if form.validate_on_submit():
            if User.query.filter_by(uname=form.uname.data).first():
                # User already exists
                flash("משתמש כבר קיים")
                return redirect(url_for('add_student'))
            hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            # add to database
            new_user = User(
                uname=form.uname.data,
                fname=form.fname.data,
                lname=form.lname.data,
                password=hash_and_salted_password,
                role='student'
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("admin_panel"))
        response = make_response(render_template("addStudent.html", form=form))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/add_stud.css"
        return response

    else:
        return abort(403)


@app.route('/edit user', methods=["POST"])
@fresh_login_required
def edit_user():
    if current_user.id == 1:
        if request.method == "POST":
            if "action2" in request.form:
                User.query.filter_by(uname=request.form["uname"]).delete()
                db.session.commit()
                return redirect(url_for("admin_panel"))
            elif "lname1" in request.form:  # lname1 is only exist in the update form
                user = User.query.filter_by(uname=request.form["uname1"]).first()
                user.fname = request.form["fname1"]
                user.lname = request.form["lname1"]
                if request.form["password1"]:
                    user.password = generate_password_hash(
                        request.form["password1"],
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                db.session.commit()
                return redirect(url_for("admin_panel"))

            elif "lname" in request.form:  # lname only exist in froms inside ther table in admin panel
                response = make_response(
                    render_template("edit_user.html", uname=request.form["uname"], fname=request.form["fname"],
                                    lname=request.form["lname"]))
                response.headers[
                    'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + css_content_policy + "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
    else:
        return abort(403)


@app.route("/add lecturer", methods=["GET", "POST"])
@fresh_login_required
def add_lecturer():
    if current_user.id == 1:
        cat = Category.query.all()  # fetch all categories from category table
        form = add_Lecturer()  # get the add lecterur form from forms.py
        form.category.choices = [(i.category, i.category) for i in
                                 cat]  # create list of sets for select input in the form
        sub_categories = []
        for i in cat:
            col_sub_category = str(i.sub_category).split("_")
            for j in col_sub_category:
                tmp = (i.category + '_' + j, j)
                sub_categories.append(tmp)

        form.tags.choices = sub_categories
        if form.validate_on_submit():
            if User.query.filter_by(uname=form.uname.data).first():
                # print(User.query.filter_by(email=form.password.data).first())
                # User already exists
                flash("משתמש כבר קיים")
                return redirect(url_for('add_lecturer'))
            hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            cati = ",".join(form.category.data)
            tags = "|".join(form.tags.data)
            if form.image.data.filename:

                lect = User(uname=form.uname.data, fname=form.fname.data, lname=form.lname.data,
                            password=hash_and_salted_password, role='lecturer', category=cati, tags=tags,
                            desc=form.desc.data,
                            image=form.image.data.filename)
                # add the lecterur image to uploads folder
                filename = secure_filename(form.image.data.filename)
                form.image.data.save('static/uploads/' + filename)
            else:
                lect = User(uname=form.uname.data, fname=form.fname.data, lname=form.lname.data,
                            password=hash_and_salted_password, role='lecturer', category=cati, tags=tags,
                            desc=form.desc.data,
                            image="avatar-g489e3d884_1280.png")
            db.session.add(lect)
            db.session.commit()
            return redirect(url_for('admin_panel'))
        response = make_response(render_template("add_lecturer.html", form=form))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + "http://127.0.0.1:5000/static/Javascript/add_lecturer.js;" + css_content_policy + "http://127.0.0.1:5000/static/css/add_stud.css"
        return response
    else:
        return abort(403)


@app.route("/edit lecturer", methods=["POST"])
@fresh_login_required
def edit_lect():
    if current_user.id == 1:
        if "action2" in request.form:
            User.query.filter_by(uname=request.form["uname"]).delete()
            db.session.commit()
            return redirect(url_for("admin_panel"))
        elif "lname1" in request.form:  # lname1 only exit in the update form
            user = User.query.filter_by(uname=request.form["uname1"]).first()
            user.fname = request.form["fname1"]
            user.lname = request.form["lname1"]
            # if type(request.form["category1"]) == "list":
            #     user.category = ",".join(request.form["category1"])
            # else:
            #     user.category = request.form["category1"]
            category_col = Category.query.all()
            user.category = ",".join([i.category for i in category_col if i.category in request.form])
            tags = []
            for i in category_col:
                for j in i.sub_category.split("_"):
                    if i.category + "_" + j in request.form:
                        tags.append(i.category + "_" + j)
            user.tags = "|".join(tags)
            user.desc = request.form["desc1"]
            if request.form["password1"]:
                user.password = generate_password_hash(
                    request.form["password1"],
                    method='pbkdf2:sha256',
                    salt_length=8
                )
            if request.files["image1"].filename:
                f = request.files["image1"]
                if user.image != "avatar-g489e3d884_1280.png":
                    os.remove("static/uploads/" + user.image)
                filename = (secure_filename(f.filename))
                f.save("static/uploads/" + filename)
                user.image = request.files["image1"].filename

            db.session.commit()
            return redirect(url_for("admin_panel"))
        elif "lname" in request.form:  # lname only exit in the form in the table in admin panel
            category_col = Category.query.all()  # fetch all categories

            category = [i.category for i in category_col]
            checked_category = request.form["category"].split(",")
            # for i in request.form["category"].split(","):
            #     if i in category:
            #         checked_category.append(i)
            sub_categories = []
            for i in category_col:
                sub_category_col = str(i.sub_category).split("_")
                for j in sub_category_col:
                    tmp = i.category + '_' + j
                    sub_categories.append(tmp)

            response = make_response(render_template("edit_lect.html", uname=request.form["uname"],
                                                     fname=request.form["fname"],
                                                     lname=request.form["lname"],
                                                     category=category,
                                                     category_len=range(len(category)),
                                                     checked_category=checked_category,
                                                     tags=sub_categories,
                                                     tags_len=range(len(sub_categories)),
                                                     checked_tags=request.form["tags"].split("|"),
                                                     image=request.form["image"],
                                                     desc=request.form["desc"],
                                                     ))
            response.headers[
                'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + css_content_policy + "http://127.0.0.1:5000/static/css/adminpanel.css "
            return response
    else:
        return abort(403)


@app.route("/add appointment", methods=["GET", "POST"])
@fresh_login_required
def add_appo():
    if current_user.role == "admin" or current_user.role == "lecturer":
        form = add_Appointment()
        if form.validate_on_submit():
            # get the date from the form⬇️
            num_date = form.appo_date.data.strftime("%Y-%m-%d")
            # get the hour from the form⬇️
            start_hour = form.appo_hour.data.strftime("%H:%M")
            # create new datatime object
            full_date = datetime.datetime(form.appo_date.data.year,
                                          form.appo_date.data.month,
                                          form.appo_date.data.day,
                                          form.appo_hour.data.hour,
                                          form.appo_hour.data.minute)
            # caluclate the time the meeting will end
            end_appo = (full_date + datetime.timedelta(minutes=int(form.appo_dur.data))).time().strftime("%H:%M")
            # check if another appoinmtment is already exist in this time⬇️
            appo_set = Appointment.query.filter_by(uname=current_user.uname, appo_date=num_date).all()
            for ap_set in appo_set:
                if ap_set.appo_start_hour <= start_hour <= ap_set.appo_end_hour \
                        or ap_set.appo_start_hour <= end_appo <= ap_set.appo_end_hour \
                        or ap_set.appo_start_hour >= start_hour and ap_set.appo_end_hour <= end_appo:
                    flash("הזמן כבר תפוס")
                    return redirect(url_for("add_appo"))
            # add appointmnet the datebase ⬇️
            new_appo = Appointment(uname=current_user.uname,
                                   fname=current_user.fname,
                                   lname=current_user.lname,
                                   appo_date=num_date,
                                   appo_start_hour=start_hour,
                                   appo_end_hour=end_appo,
                                   appo_loc=htmlentities.encode(form.appo_loc.data),
                                   appo_type=htmlentities.encode(form.appo_type.data),
                                   appo_limit=form.appo_limit.data,
                                   appo_dur=form.appo_dur.data)
            db.session.add(new_appo)
            db.session.commit()
            return redirect(url_for("lecturer_panel"))

        response = make_response(render_template("add_appointment.html", form=form))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/add_appo.css"
        return response
    else:
        return abort(403)


@app.route("/main", methods=["GET", "POST"])
@fresh_login_required
def set_appo():  # main
    # category_col = Category.query.all()
    user_cat = User.query.filter_by(role="lecturer").all()
    catgories = []
    for i in user_cat:
        if "," in i.category:
            for j in i.category.split(","):
                catgories.append(j)
        else:
            catgories.append(i.category)
    catgories = list(set(catgories))  # create list for the categories buttons
    tags = []
    for i in user_cat:
        try:
            if "|" in i.tags:
                for j in i.tags.split("|"):
                    tags.append(j)
            else:
                tags.append(i.tags)
        except:
            continue
    tags = list(set(tags))
    if request.method == "POST" and "record" in request.form:  # if the user want the records of the category he choose
        records = Record.query.filter_by(category=request.form["record"]).all()
        record_cat = request.form["record"]
        records_len = range(len(records))
        response = make_response(
            render_template("main.html", len_tags=range(len(tags)), records_len=records_len, records=records,
                            record_cat=record_cat, cat=catgories, user_cat=user_cat, tags=tags,
                            len_cat=range(len(catgories)), ))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/main.css"
        return response
    if request.method == "POST" and "ap_date" in request.form:  # if the user order appointment
        add_user_to_appo = Appointment.query.filter_by(uname=request.form["ap_uname"],
                                                       appo_date=request.form["ap_date"],
                                                       appo_start_hour=request.form["ap_hour_st"]).first()
        if add_user_to_appo.appo_user_aproved:
            if add_user_to_appo.appo_user_wait.find(
                    "\n" + current_user.uname + " ") != -1 or add_user_to_appo.appo_user_aproved.find(
                "\n" + current_user.uname + " ") != -1:  # if the user already approved or wait
                response = make_response(
                    render_template("main.html", cat=catgories, user_cat=user_cat, tags=tags, found=""))
                response.headers[
                    'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/main.css"
                return response

        if add_user_to_appo.appo_user_wait:
            add_user_to_appo.appo_user_wait = add_user_to_appo.appo_user_wait + "\n" + current_user.fname + " " + current_user.lname + " " + current_user.uname + " " + htmlentities.encode(
                request.form["ap_com"])  # if the appo_user_wait already have users
        else:
            add_user_to_appo.appo_user_wait = "\n" + current_user.fname + " " + current_user.lname + " " + current_user.uname + " " + \
                                              htmlentities.encode(request.form["ap_com"])  # if this is the first uder
        db.session.commit()
        response = make_response(
            render_template("main.html", len_tags=range(len(tags)), cat=catgories, user_cat=user_cat,
                            len_cat=range(len(catgories)), tags=tags, found="", records=""))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/main.css"
        return response
    elif request.method == "POST":
        d = datetime.datetime.now()
        found = User.query.filter_by(uname=request.form["val"]).all()  # get details about the lecterur
        appo_user = Appointment.query.filter_by(uname=request.form["val"]).order_by(Appointment.appo_date,
                                                                                    Appointment.appo_start_hour).all()  # get all appointments
        month_appo = []  # get all appointments available in the current month ⬇️
        for i in appo_user:
            if i.appo_date.split("-")[1] == str(d.month) and i.appo_date.split("-")[0] == str(d.year):
                month_appo.append(i)
            elif i.appo_date.split("-")[1][1] == str(d.month) and i.appo_date.split("-")[0] == str(d.year):
                month_appo.append(i)
        # creating a calendar⬇️
        cal = calendar.HTMLCalendar(firstweekday=6)  # day 6 is sunday
        cal = cal.formatmonth(d.year, d.month)
        # change the days name to hebrew ⬇️
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        h_days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]  # change the days name to hebrew
        for i in range(7):
            cal = cal.replace(days[i], h_days[i], 1)
        # end the day name change
        # split the days for using modal⬇️
        cal = cal.split("<td ")
        tmp_lst = []  # tmp_lst is used for storage the dates and hour_lst_string in this format[day of date,meeting hours] for example ["03","aaaaA","22","bbbb"]
        hour_lst_string = ""  # hour lst string is ther button for call the modal
        for i in range(len(cal)):  # check every table cell in the calender table
            for check_appo in month_appo:
                tmp_date = check_appo.appo_date.split("-")[2]
                if tmp_date in cal[i]:
                    if check_appo.appo_user_aproved:
                        if len(check_appo.appo_user_aproved.split("\n")[
                               1:]) == check_appo.appo_limit:  # if the meeting is full and all users approved
                            hour_lst_string = functions.main_page.red(check_appo)
                        elif len(check_appo.appo_user_aproved.split("\n")[1:]) + len(
                                check_appo.appo_user_wait.split("\n")[
                                1:]) == check_appo.appo_limit:  # if the users wait for approve is full
                            hour_lst_string = functions.main_page.yellow(check_appo)
                        else:
                            hour_lst_string = functions.main_page.green(check_appo)  # if the meeting isnt full
                    elif check_appo.appo_user_wait:  # if the users wait for approve is full
                        if len(check_appo.appo_user_wait.split("\n")) == check_appo.appo_limit:
                            hour_lst_string += functions.main_page.yellow(check_appo)
                        else:  # if the meeting isnt full
                            hour_lst_string = functions.main_page.green(check_appo)
                    else:  # if the meeting isnt full
                        hour_lst_string += functions.main_page.green(check_appo)
                    if tmp_date not in tmp_lst:  # add the date to tmp_lst
                        tmp_lst.append(tmp_date)
                elif tmp_date[1] in cal[i] and check_appo.appo_date.split("-")[2][0] == "0":
                    # in case the date is 1,2,3,4,5,6,7,8,9 becuase the dates save as 01,02,03...⬆
                    if check_appo.appo_user_aproved:
                        if len(check_appo.appo_user_aproved.split("\n")[1:]) == check_appo.appo_limit:
                            hour_lst_string = functions.main_page.red(check_appo)
                        elif len(check_appo.appo_user_aproved.split("\n")[1:]) + len(
                                check_appo.appo_user_wait.split("\n")[1:]) == check_appo.appo_limit:
                            hour_lst_string = functions.main_page.yellow(check_appo)
                        else:
                            hour_lst_string = functions.main_page.green(check_appo)
                    elif check_appo.appo_user_wait:
                        if len(check_appo.appo_user_wait.split("\n")[1:]) == check_appo.appo_limit:
                            hour_lst_string += functions.main_page.yellow(check_appo)
                        else:
                            hour_lst_string = functions.main_page.green(check_appo)
                    else:
                        hour_lst_string += functions.main_page.green(check_appo)
                    if tmp_date not in tmp_lst:  # add the date to tmp_lst
                        tmp_lst.append(tmp_date)
                for j in range(len(tmp_lst)):  # storage all the dates and hour_lst_string

                    if tmp_date == tmp_lst[j]:  # if the date in the list
                        if j + 1 == len(tmp_lst):  # if this is the first appo found create new index
                            tmp_lst.append(hour_lst_string)
                        else:
                            tmp_lst[j + 1] += hour_lst_string  # else add the meeting to eleemnt value
                        hour_lst_string = ""
            for j in range(0, len(tmp_lst), 2):  # add to dropdown menu
                if tmp_lst[j][0] == "0":  # in case the date is 01,02,03,04
                    tmp_lst[j] = tmp_lst[j][1]
                cal[i] = cal[i].replace(">" + tmp_lst[j],
                                        "><div class='dropdown'><button type='button' class='btn btn-primary dropdown-toggle' data-bs-toggle='dropdown'>" +
                                        tmp_lst[j] + "</button>\n<ul class='dropdown-menu'>" + tmp_lst[
                                            j + 1] + "</ul></div>")  # create dropdown menu with the hours for every day meeting is available
                hour_lst_string = ""
        cal = "<td ".join(cal)
        response = make_response(
            render_template("main.html", len_tags=range(len(tags)), cat=catgories, user_cat=user_cat, tags=tags,
                            len_cat=range(len(catgories)), found=found,
                            caln=cal.replace('<td ', '<td  width="150" height="150"'),
                            month_appo=month_appo))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/main.css"
        return response

    response = make_response(
        render_template("main.html", len_tags=range(len(tags)), cat=catgories, user_cat=user_cat, tags=tags,
                        len_cat=range(len(catgories)), found="", records=""))
    response.headers[
        'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/main.css"
    return response


@app.route("/lect panel", methods=["GET", "POST"])
@fresh_login_required
def lecturer_panel():
    if current_user.role == "admin" or current_user.role == "lecturer":
        if request.method == "POST":
            if request.form[
                "action"] == "אישור":  # delete the users from the waiting to approve column in the row of the appoinntment and add the user the approved users for the appointment
                appo_approve = Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                           appo_start_hour=request.form["ap_hour_st"]).first()
                if appo_approve.appo_user_aproved:
                    appo_approve.appo_user_aproved = appo_approve.appo_user_aproved + "\n" + request.form["add_user"]
                    appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace("\n" + request.form["add_user"],
                                                                                      "")

                else:
                    appo_approve.appo_user_aproved = "\n" + request.form["add_user"]
                    appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace("\n" + request.form["add_user"],
                                                                                      "")
                db.session.commit()
                return redirect(url_for("lecturer_panel"))
            elif request.form["action"] == "דחייה":  # delete the users from the waiting to approve column in the row of the
                # appoinntment
                appo_rej = Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                       appo_start_hour=request.form["ap_hour_st"]).first()
                appo_rej.appo_user_wait = appo_rej.appo_user_wait.replace("\n" + request.form["add_user"], "")
                db.session.commit()
                redirect(url_for("lecturer_panel"))
            elif request.form["action"] == "מחק":  # delete the users from the approved users for the appointment
                appo_del = Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                       appo_start_hour=request.form["ap_hour_st"]).first()
                appo_del.appo_user_aproved = appo_del.appo_user_aproved.replace("\n" + request.form["del_user"], "")
                if not appo_del.appo_user_aproved:
                    appo_del.appo_user_aproved == ""
                db.session.commit()
                return redirect(url_for("lecturer_panel"))

        appo_user = Appointment.query.filter_by(uname=current_user.uname).order_by(Appointment.appo_date,
                                                                                   Appointment.appo_start_hour).all()  # get all user appointments
        table_len = range(len(appo_user))
        # for i in table_len:
        #     if appo_user[i].appo_user_wait:  # change the appo_user_wait and appo_user_aproved columns to lists
        #         temp = appo_user[i].appo_user_wait.replace("\n", "")
        #         if temp:
        #             appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.split("\n")[1:]
        #             appo_user[i].appo_user_wait.append(len(appo_user[i].appo_user_wait))
        #         else:
        #             appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.replace("\n", "")
        #     if appo_user[i].appo_user_aproved:
        #         temp = appo_user[i].appo_user_aproved.replace("\n", "")
        #         if temp:
        #             appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.split("\n")[1:]
        #             appo_user[i].appo_user_aproved.append(len(appo_user[i].appo_user_aproved))
        #         else:
        #             appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.replace("\n", "")
        for i in table_len:
            if appo_user[i].appo_user_wait:  # if its not none
                temp = appo_user[i].appo_user_wait.replace("\n", "")
                if temp:
                    appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.split("\n")[
                                                  1:]  # the users in appo_user_wait save \n name...\n name \n ..... so get list of all users i split by \n
                    appo_user[i].appo_user_wait.append(len(appo_user[
                                                               i].appo_user_wait))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                else:
                    appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.replace("\n",
                                                                                      "")  # else if no user wait for approve the objects value become to "" which is nothing
            if appo_user[i].appo_user_aproved:  # if its not none
                temp = appo_user[i].appo_user_aproved.replace("\n", "")
                if temp:
                    appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.split("\n")[
                                                     1:]  # the users in appo_user_aproved save \n name...\n name \n ..... so get list of all users i split by \n
                    appo_user[i].appo_user_aproved.append(len(appo_user[
                                                                  i].appo_user_aproved))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                else:
                    appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.replace("\n",
                                                                                            "")  # else if no user wait for approve the objects value become to "" which is nothing
        response = make_response(
            render_template("lecturer_panel.html", table_len=table_len, appo_user=appo_user, current_user=current_user))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
        return response
    else:
        return abort(403)


@app.route("/edit appo", methods=["POST"])
@fresh_login_required
def edit_appo():
    if current_user.role == "admin" or current_user.role == "lecturer":
        # update appointment details⬇️
        if "ap_date1" in request.form:
            # num_date = request.form["ap_date1"].strftime("%Y-%m-%d")
            splited_date = request.form["ap_date1"].split("-")
            if len(splited_date) != 3:
                return abort(403)

            start_hour = request.form["ap_hour_st1"]
            start_hour_split = request.form["ap_hour_st1"].split(":")
            if len(start_hour_split) != 2:
                return abort(403)
            try:

                full_date = datetime.datetime(int(splited_date[0]),
                                              int(splited_date[1]),
                                              int(splited_date[2]),
                                              int(start_hour_split[0]),
                                              int(start_hour_split[1]))
            except:
                return abort(403)

            end_appo = (full_date + datetime.timedelta(minutes=int(request.form["ap_dur1"]))).time().strftime("%H:%M")
            appo_set = Appointment.query.filter_by(uname=request.form["lect"], appo_date=request.form["ap_date1"]).all()
            for ap_set in appo_set:
                if (ap_set.appo_start_hour <= start_hour <= ap_set.appo_end_hour) \
                        or (ap_set.appo_start_hour <= end_appo <= ap_set.appo_end_hour) \
                        or (ap_set.appo_start_hour >= start_hour and ap_set.appo_end_hour <= end_appo):
                    if ap_set.id != int(request.form["id"]):
                        response = make_response(render_template("edit_appo.html",
                                                                 ap_date=request.form["ap_date1"],
                                                                 ap_hour_st=request.form["ap_hour_st1"],
                                                                 ap_dur=request.form["ap_dur1"],
                                                                 ap_loc=request.form["ap_loc1"],
                                                                 ap_limit=request.form["appo_limit1"],
                                                                 ap_type=request.form["appo_type1"],
                                                                 ap_id=request.form["id"],
                                                                 ty=["פרטני", "קבוצה"], error="הזמן כבר תפוס",
                                                                 current_user=current_user))
                        response.headers[
                            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
                        return response

            up_appo = Appointment.query.filter_by(id=request.form["id"]).first()
            if up_appo.appo_date != request.form[
                "ap_date1"] or up_appo.uname != current_user.uname and current_user.id != 1:
                return abort(403)
            up_appo.appo_date = request.form["ap_date1"]
            up_appo.appo_start_hour = request.form["ap_hour_st1"]
            up_appo.appo_dur = request.form["ap_dur1"]
            up_appo.appo_loc = request.form["ap_loc1"]
            up_appo.appo_end_hour = end_appo
            up_appo.appo_limit = request.form["appo_limit1"]
            up_appo.appo_type = request.form["appo_type1"]
            db.session.commit()
            if current_user.id == 1:
                return redirect(url_for("admin_panel"))

            return redirect(url_for("lecturer_panel"))
        elif "ap_date" in request.form:
            if request.form["action2"] == "ערוך פגישה זאת":  # go to update details webpage
                if "lect_name" in request.form and current_user.id == 1:

                    up_appo = Appointment.query.filter_by(uname=request.form["lect_name"],
                                                          appo_date=request.form["ap_date"],
                                                          appo_start_hour=request.form["ap_hour_st"]).first()
                else:
                    up_appo = Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                          appo_start_hour=request.form["ap_hour_st"]).first()
                response = make_response(render_template("edit_appo.html",
                                                         lect=up_appo.uname,
                                                         ap_id=up_appo.id,
                                                         ap_date=request.form["ap_date"],
                                                         ap_hour_st=request.form["ap_hour_st"],
                                                         ap_dur=request.form["ap_dur"],
                                                         ap_loc=request.form["ap_loc"],
                                                         ap_limit=request.form["ap_limit"],
                                                         ap_type=request.form["ap_type"],
                                                         ty=["פרטני", "קבוצה"], current_user=current_user))
                response.headers[
                    'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
                return response

            elif request.form["action2"] == "שלח הודעה":  # send message for all students
                if "lect_name" in request.form and current_user.id == 1:

                    up_appo = Appointment.query.filter_by(uname=request.form["lect_name"],
                                                          appo_date=request.form["ap_date"],
                                                          appo_start_hour=request.form["ap_hour_st"]).first()
                else:
                    up_appo = Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                          appo_start_hour=request.form["ap_hour_st"]).first()
                response = make_response(render_template("send_msg.html",
                                                         lect=up_appo.uname,
                                                         ap_id=up_appo.id,
                                                         ap_date=request.form["ap_date"],
                                                         ap_hour_st=request.form["ap_hour_st"],
                                                         ap_loc=request.form["ap_loc"], appo_msg=request.form["msgs"],
                                                         current_user=current_user))
                response.headers[
                    'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + " http://127.0.0.1:5000/static/css/send_msg.css "
                return response
            elif request.form["action2"] == "מחק":  # delete appointment
                if "lect_name" in request.form and current_user.id == 1:

                    Appointment.query.filter_by(uname=request.form["lect_name"],
                                                appo_date=request.form["ap_date"],
                                                appo_start_hour=request.form["ap_hour_st"]).delete()
                    db.session.commit()
                    return redirect(url_for("admin_panel"))
                else:
                    Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                appo_start_hour=request.form["ap_hour_st"]).delete()
                    db.session.commit()
                    return redirect(url_for("lecturer_panel"))
    else:
        return abort(403)


@app.route("/add record", methods=["POST", "GET"])
@fresh_login_required
def add_rec():
    if current_user.role == "admin":
        # classic add item in this case record(record category,tags,record title,record link,record description)
        cat = Category.query.all()  # fetch all categories from category table
        form = add_record()
        form.record_category.choices = [(i.category, i.category) for i in cat]
        sub_categories = []
        for i in cat:
            col_sub_category = str(i.sub_category).split("_")
            for j in col_sub_category:
                tmp = (i.category + '_' + j, j)
                sub_categories.append(tmp)

        form.tags.choices = sub_categories
        if form.validate_on_submit():
            new_record = Record(category=",".join(form.record_category.data),
                                tags="|".join(form.tags.data),
                                title=form.record_title.data,
                                link=form.record_link.data,
                                desc=form.record_desc.data)
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('admin_panel'))

        response = make_response(render_template("add_record.html", form=form))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + "http://127.0.0.1:5000/static/Javascript/add_record.js" + ";" + css_content_policy + ";"
        return response
    else:
        return abort(403)


@app.route("/edit record", methods=["POST"])
@fresh_login_required
def edit_rec():
    if current_user.id == 1:
        if request.method == "POST":
            if "action2" in request.form:  # update the record
                Record.query.filter_by(link=request.form["rec_link"]).delete()
                db.session.commit()
                return redirect(url_for("admin_panel"))
            elif "title1" in request.form:  # title1 is only exist in the update form
                rec = Record.query.filter_by(id=request.form["id1"]).first()
                records = Record.query.all()
                category_col = Category.query.all()
                rec.category = ",".join([i.category for i in category_col if i.category in request.form])
                tags = []
                for i in category_col:
                    for j in i.sub_category.split("_"):
                        if i.category + "_" + j in request.form:
                            tags.append(i.category + "_" + j)
                rec.tags = "|".join(tags)

                category = [i.category for i in category_col]
                checked_category = [i.category for i in category_col if i.category in request.form]
                # for i in request.form["category"].split(","):
                #     if i in category:
                #         checked_category.append(i)
                sub_categories = []
                for i in category_col:
                    sub_category_col = str(i.sub_category).split("_")
                    for j in sub_category_col:
                        tmp = i.category + '_' + j
                        sub_categories.append(tmp)
                for i in records:
                    if i.link == request.form["link1"] and i.id != int(request.form["id1"]):
                        response = make_response(render_template("edit_record.html", category=category,
                                                                 category_len=range(len(category)),
                                                                 checked_category=checked_category,
                                                                 tags=sub_categories,
                                                                 tags_len=range(len(sub_categories)),
                                                                 link=request.form["link1"],
                                                                 desc=request.form["desc1"],
                                                                 title=request.form["title1"],
                                                                 rec_id1=request.form["id1"],
                                                                 error="הקלטה זאת נמצאת כבר"))
                        response.headers[
                            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
                        return response

                rec.link = request.form["link1"]
                rec.desc = request.form["desc1"]
                rec.title = request.form["title1"]
                db.session.commit()
                return redirect(url_for("admin_panel"))
            elif "rec_title" in request.form:  # rec_title only exist in froms inside the table in admin panel,redirect to edit record
                category_col = Category.query.all()  # fetch all categories

                category = [i.category for i in category_col]
                checked_category = request.form["rec_category"].split(",")
                # for i in request.form["category"].split(","):
                #     if i in category:
                #         checked_category.append(i)
                sub_categories = []
                for i in category_col:
                    sub_category_col = str(i.sub_category).split("_")
                    for j in sub_category_col:
                        tmp = i.category + '_' + j
                        sub_categories.append(tmp)
                rec_id = Record.query.filter_by(link=request.form["rec_link"]).first().id
                response = make_response(render_template("edit_record.html", category=category,
                                                         category_len=range(len(category)),
                                                         checked_category=checked_category,
                                                         tags=sub_categories,
                                                         tags_len=range(len(sub_categories)),
                                                         checked_tags=request.form["rec_tags"].split("|"),
                                                         link=request.form["rec_link"],
                                                         desc=request.form["rec_desc"],
                                                         title=request.form["rec_title"],
                                                         rec_id1=rec_id))
                response.headers[
                    'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
                return response
    else:
        return abort(403)


@app.route("/admin profile", methods=["POST", "GET"])
@fresh_login_required
def admin_profile():
    # classic update profile
    if current_user.id == 1:
        if request.method == "POST":

            if request.form["password1"]:
                user = User.query.filter_by(id=1).first()
                user.password = generate_password_hash(
                    request.form["password1"],
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                with open("passwords.txt", "w") as f:
                    f.write(request.form["password1"])
            db.session.commit()
            return redirect(url_for("admin_panel"))

        response = make_response(render_template("admin_profile.html"))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
        return response
    else:
        return abort(403)


@app.route('/student profile', methods=["POST", "GET"])
@fresh_login_required
def stu_profile():
    if current_user.role == "student" or current_user.role == "admin":
        if request.method == "POST":
            if "lname1" in request.form:
                user = User.query.filter_by(uname=current_user.uname).first()
                user.fname = request.form["fname1"]
                user.lname = request.form["lname1"]
                if request.form["password1"]:
                    user.password = generate_password_hash(
                        request.form["password1"],
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                db.session.commit()
                return redirect(url_for("set_appo"))
        user = User.query.filter_by(uname=current_user.uname).first()
        user_appos = Appointment.query.filter(
            Appointment.appo_user_aproved.like("% " + current_user.uname + " %")).order_by(Appointment.appo_date,
                                                                                           Appointment.appo_start_hour).all()  # get all appointments of current user
        table_len = range(len(user_appos))

        response = make_response(render_template("student_profile.html", uname=user.uname, fname=user.fname,
                                                 lname=user.lname, user_appos=user_appos, table_len=table_len))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
        return response
    else:
        return abort(403)


@app.route("/lecterur profile", methods=["POST", "GET"])
@fresh_login_required
def lect_profile():
    # this the classic update profile
    if current_user.role == "lecturer":
        if "POST" == request.method:  # lname1 only exit in the update form
            user = User.query.filter_by(uname=request.form["uname1"]).first()
            user.fname = request.form["fname1"]
            user.lname = request.form["lname1"]
            user.desc = request.form["desc1"]
            if request.form["password1"]:
                user.password = generate_password_hash(
                    request.form["password1"],
                    method='pbkdf2:sha256',
                    salt_length=8
                )
            if request.files["image1"].filename:
                f = request.files["image1"]
                filename = (secure_filename(f.filename))
                f.save("static/uploads/" + filename)
                user.image = request.files["image1"].filename

            db.session.commit()
            return redirect(url_for("lecturer_panel"))

        lect_info = User.query.filter_by(uname=current_user.uname).first()
        response = make_response(render_template("lect_profile.html", lect_info=lect_info))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
        return response
    else:
        return abort(403)


@app.route("/del_appo", methods=["POST"])
@fresh_login_required
def delete_from_appo():
    if current_user.role == "student":
        if request.method == "POST":
            appo_del = Appointment.query.filter_by(uname=request.form["lect_name"],
                                                   appo_date=request.form["ap_date"],
                                                   appo_start_hour=request.form[
                                                       "ap_hour_st"]).first()  # get appointment
            appo_del.appo_user_aproved = appo_del.appo_user_aproved.replace(
                "\n" + current_user.fname + " " + current_user.lname + " " + current_user.uname, "")  # delete the user
            if not appo_del.appo_user_aproved:
                appo_del.appo_user_aproved == ""
            db.session.commit()
        return redirect(url_for('stu_profile'))
    else:
        return abort(403)


@app.route("/send msg", methods=["POST"])
@fresh_login_required
def sendmsg():
    if current_user.role == "lecturer" or current_user.role == "admin":
        curr_appo = Appointment.query.filter_by(uname=request.form["lect"],
                                                appo_date=request.form["ap_date1"],
                                                appo_start_hour=request.form[
                                                    "ap_hour_st1"]).first()  # get appointment by lecturer date and hour
        curr_appo.appo_msg = request.form["text"]  # create new message
        db.session.commit()
        if current_user.id == 1:
            return redirect(url_for('admin_panel'))
        return redirect(url_for("lecturer_panel"))
    else:
        return abort(403)


@app.route("/add category", methods=["GET", "POST"])
@fresh_login_required
def add_cat():
    if current_user.role == "admin":
        form = add_category()
        if form.validate_on_submit():
            if form.sub_category.data != '':

                new_cat = Category(category=form.category.data, sub_category=form.sub_category.data)
            else:
                new_cat = Category(category=form.category.data)
            db.session.add(new_cat)
            db.session.commit()
            return redirect(url_for('admin_panel'))

        response = make_response(render_template("add_category.html", form=form))
        response.headers[
            'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + ";"
        return response
    else:
        return abort(403)


@app.route("/search", methods=["POST"])
@fresh_login_required
def search():
    # user_cat = User.query.filter_by(role="lecturer").all()
    result = User.query.filter(User.tags.contains(request.form["tag"])).all()
    response = make_response(render_template("search.html", lecturers=result))
    response.headers[
        'Content-Security-Policy'] = defualt_content_policy + ";" + js_content_policy + ";" + css_content_policy + "http://127.0.0.1:5000/static/css/main.css" + ";"
    return response


if __name__ == '__main__':
    app.run(debug=True)
