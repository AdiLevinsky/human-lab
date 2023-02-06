from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash

import app

student_profile_bp = Blueprint("student_profile", __name__)


@student_profile_bp.route('/student profile', methods=["POST", "GET"])
@fresh_login_required
def student_profile():
    if current_user.role == "student" or current_user.role == "admin":
        if request.method == "POST":
            if "lname1" in request.form:
                user = app.User.query.filter_by(uname=current_user.uname).first()
                user.fname = request.form["fname1"]
                user.lname = request.form["lname1"]
                if request.form["password1"]:
                    user.password = generate_password_hash(
                        request.form["password1"],
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                app.db.session.commit()
                return redirect(url_for("set_appointment.set_appointment"))
        user = app.User.query.filter_by(uname=current_user.uname).first()
        user_appos = app.Appointment.query.filter(
            app.Appointment.appo_user_aproved.like("% " + current_user.uname + " %")).order_by(
            app.Appointment.appo_date,
            app.Appointment.appo_start_hour).all()  # get all appointments of current user
        table_len = range(len(user_appos))

        response = make_response(render_template("student_profile.html", uname=user.uname, fname=user.fname,
                                                 lname=user.lname, user_appos=user_appos, table_len=table_len))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
