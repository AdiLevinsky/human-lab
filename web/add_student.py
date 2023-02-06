from flask import render_template, redirect, url_for, flash, abort, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash

import app
from forms import add_student as add_student_form

add_student_bp = Blueprint("add_student", __name__)


@add_student_bp.route('/add studet', methods=["GET", "POST"])
@fresh_login_required
def add_student():
    if current_user.id == 1:
        form = add_student_form()  # call the add student form from forms.py
        if form.validate_on_submit():
            if app.User.query.filter_by(uname=form.uname.data).first():
                # User already exists
                flash("משתמש כבר קיים")
                return redirect(url_for('add_student.add_student'))
            hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            # add to database
            new_user = app.User(
                uname=form.uname.data,
                fname=form.fname.data,
                lname=form.lname.data,
                password=hash_and_salted_password,
                role='student'
            )
            app.db.session.add(new_user)
            app.db.session.commit()
            return redirect(url_for("admin_panel.admin_panel"))
        response = make_response(render_template("addStudent.html", form=form))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + "http://127.0.0.1:5000/static/css/add_stud.css"
        return response

    else:
        return abort(403)
