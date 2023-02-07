from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash

import app

edit_user_bp = Blueprint("edit_user", __name__)


@edit_user_bp.route('/edit user', methods=["POST"])
@fresh_login_required
def edit_user():
    if current_user.id == 1:
        if request.method == "POST":
            if "action2" in request.form:
                app.User.query.filter_by(uname=request.form["uname"]).delete()
                app.db.session.commit()
                return redirect(url_for("admin_panel.admin_panel"))
            elif "lname1" in request.form:  # lname1 is only exist in the update form
                user = app.User.query.filter_by(uname=request.form["uname1"]).first()
                user.fname = request.form["fname1"]
                user.lname = request.form["lname1"]
                if request.form["password1"]:
                    user.password = generate_password_hash(
                        request.form["password1"],
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                app.db.session.commit()
                return redirect(url_for("admin_panel.admin_panel"))

            elif "lname" in request.form:  # lname only exist in froms inside ther table in admin panel
                response = make_response(
                    render_template("edit_user.html", uname=request.form["uname"], fname=request.form["fname"],
                                    lname=request.form["lname"]))

                response.headers[
                    'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                return response
    else:
        return abort(403)
