import datetime

import htmlentities
import pytz
from flask import render_template, redirect, url_for, flash, make_response, Blueprint
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash

import app
from forms import LoginForm

login_bp = Blueprint("login", __name__)

tz = pytz.timezone("Asia/Tel_Aviv")
@login_bp.route("/", methods=["POST", "GET"])
def login():  # put application's code here
    # for auto delete of old appoitmnets
    appo_user = app.Appointment.query.order_by(app.Appointment.appo_date,
                                               app.Appointment.appo_start_hour).all()
    for i in range(len(appo_user)):
        if appo_user[i].appo_date < datetime.datetime.now(tz).strftime("%Y-%m-%d") or appo_user[i].appo_date \
                == datetime.datetime.now(tz).strftime("%Y-%m-%d") \
                and appo_user[i].appo_start_hour < datetime.datetime.now(tz).strftime("%H:%M"):
            app.Appointment.query.filter_by(id=appo_user[i].id).delete()
            app.db.session.commit()

    if not current_user.is_authenticated:  # if the user isn't log in
        form = LoginForm()  # call the login form from forms.py
        if form.validate_on_submit():
            uname = htmlentities.encode(form.uname.data)  # prevent xss
            password = htmlentities.encode(form.password.data)  # prevent xss

            user = app.User.query.filter_by(uname=uname).first()
            # Email doesn't exist or password incorrect.
            if not user:
                flash("משתמש לא קיים")
                return redirect(url_for('login.login'))
            elif not check_password_hash(user.password, password):
                flash('סיסמה לא נכונה נסה שוב')
                return redirect(url_for('login.login'))
            else:
                # redrect by role
                login_user(user)
                if current_user.role == "admin":
                    return redirect(url_for('admin_panel.admin_panel'))
                if current_user.role == "lecturer":
                    return redirect(url_for("lecturer_panel.lecturer_panel"))
                return redirect(url_for("set_appointment.set_appointment"))
        # response = make_response(render_template(url_for('templates',filename='index.html'), form=form))
        response = make_response(render_template('index.html', form=form))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:  # if the use log in
        if current_user.role == "admin":
            return redirect(url_for('admin_panel.admin_panel'))
        if current_user.role == "lecturer":
            return redirect(url_for("lecturer_panel.lecturer_panel"))
        return redirect(url_for("set_appointment.set_appointment"))
