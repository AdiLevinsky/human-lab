from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

import app

lecturer_profile_bp = Blueprint("lecturer_profile", __name__)


@lecturer_profile_bp.route("/lecturer profile", methods=["POST", "GET"])
@fresh_login_required
def lecturer_profile():
    # this the classic update profile
    if current_user.role == "lecturer":
        if "POST" == request.method:  # lname1 only exit in the update form
            user = app.User.query.filter_by(uname=request.form["uname1"]).first()
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

            app.db.session.commit()
            return redirect(url_for("lecturer_panel.lecturer_panel"))

        lect_info = app.User.query.filter_by(uname=current_user.uname).first()
        response = make_response(render_template("lect_profile.html", lect_info=lect_info))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
