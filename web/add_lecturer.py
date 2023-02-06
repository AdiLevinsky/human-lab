from flask import render_template, redirect, url_for, flash, abort, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

import app
from forms import add_Lecturer

add_lecturer_bp = Blueprint("add_lecturer", __name__)


@add_lecturer_bp.route("/add lecturer", methods=["GET", "POST"])
@fresh_login_required
def add_lecturer():
    if current_user.id == 1:
        cat = app.Category.query.all()  # fetch all categories from category table
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
            if app.User.query.filter_by(uname=form.uname.data).first():
                # print(User.query.filter_by(email=form.password.data).first())
                # User already exists
                flash("משתמש כבר קיים")
                return redirect(url_for('add_lecturer.add_lecturer'))
            hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            cati = ",".join(form.category.data)
            tags = "|".join(form.tags.data)
            if form.image.data.filename:

                lect = app.User(uname=form.uname.data, fname=form.fname.data, lname=form.lname.data,
                                password=hash_and_salted_password, role='lecturer', category=cati, tags=tags,
                                desc=form.desc.data,
                                image=form.image.data.filename)
                # add the lecterur image to uploads folder
                filename = secure_filename(form.image.data.filename)
                form.image.data.save('static/uploads/' + filename)
            else:
                lect = app.User(uname=form.uname.data, fname=form.fname.data, lname=form.lname.data,
                                password=hash_and_salted_password, role='lecturer', category=cati, tags=tags,
                                desc=form.desc.data,
                                image="avatar-g489e3d884_1280.png")
            app.db.session.add(lect)
            app.db.session.commit()
            return redirect(url_for('admin_panel.admin_panel'))
        response = make_response(render_template("add_lecturer.html", form=form))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + "http://127.0.0.1:5000/static/Javascript/add_lecturer.js;" + app.css_content_policy + "http://127.0.0.1:5000/static/css/add_stud.css"
        return response
    else:
        return abort(403)
