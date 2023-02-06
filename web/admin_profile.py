from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash

import app

admin_profile_bp = Blueprint("admin_profile", __name__)


@admin_profile_bp.route("/admin profile", methods=["POST", "GET"])
@fresh_login_required
def admin_profile():
    # classic update profile
    if current_user.id == 1:
        if request.method == "POST":

            if request.form["password1"]:
                user = app.User.query.filter_by(id=1).first()
                user.password = generate_password_hash(
                    request.form["password1"],
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                with open("passwords.txt", "w") as f:
                    f.write(request.form["password1"])
            app.db.session.commit()
            return redirect(url_for("admin_panel.admin_panel"))

        response = make_response(render_template("admin_profile.html"))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
