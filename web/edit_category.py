from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app

edit_category_bp = Blueprint("edit_category", __name__)


@edit_category_bp.route("/edit category", methods=["POST"])
@fresh_login_required
def edit_category():
    if current_user.id == 1:
        if request.method == "POST":
            if "cat_id" in request.form:  # title1 is only exist in the update form
                category = app.Category.query.filter_by(id=request.form["cat_id"]).first()

                changed_sub_categories = "_".join(set(request.form["tags"].split("_")))

                category.sub_category = changed_sub_categories
                app.db.session.commit()
                return redirect(url_for("admin_panel.admin_panel"))

                app.db.session.commit()
                return redirect(url_for("admin_panel.admin_panel"))
            elif "sub_categories" in request.form:  # rec_title only exist in froms inside the table in admin panel,redirect to edit record
                category1 = app.Category.query.filter_by(
                    category=request.form["category"]).first()  # fetch all categories
                response = make_response(
                    render_template("edit_category.html", cat_id=category1.id, category=request.form["category"],
                                    tags=category1.sub_category, ))
                response.headers[
                    'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                return response
    else:
        return abort(403)
