import os

from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

import app

edit_lecturer_bp = Blueprint("edit_lecturer", __name__)


@edit_lecturer_bp.route("/edit lecturer", methods=["POST"])
@fresh_login_required
def edit_lecturer():
    if current_user.id == 1:
        if "action2" in request.form:
            app.User.query.filter_by(uname=request.form["uname"]).delete()
            app.db.session.commit()
            return redirect(url_for("admin_panel.admin_panel"))
        elif "lname1" in request.form:  # lname1 only exit in the update form
            user = app.User.query.filter_by(uname=request.form["uname1"]).first()
            user.fname = request.form["fname1"]
            user.lname = request.form["lname1"]
            category_col = app.Category.query.all()
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

            app.db.session.commit()
            return redirect(url_for("admin_panel.admin_panel"))
        elif "lname" in request.form:  # lname only exit in the form in the table in admin panel
            category_col = app.Category.query.all()  # fetch all categories

            category = [i.category for i in category_col]
            checked_category = request.form["category"].split(",")
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
                'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + app.css_content_policy + "http://127.0.0.1:5000/static/css/adminpanel.css "
            return response
    else:
        return abort(403)
