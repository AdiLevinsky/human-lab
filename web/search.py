from flask import render_template, request, make_response, Blueprint
from flask_login import fresh_login_required

import app

search_bp = Blueprint("search", __name__)


@search_bp.route("/search", methods=["POST"])
@fresh_login_required
def search():
    # user_cat = User.query.filter_by(role="lecturer").all()
    result = app.User.query.filter(app.User.tags.contains(request.form["tag"])).all()
    response = make_response(render_template("search.html", lecturers=result))
    response.headers[
        'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + "http://127.0.0.1:5000/static/css/main.css" + ";"
    return response
