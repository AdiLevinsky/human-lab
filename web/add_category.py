from flask import render_template, redirect, url_for, abort, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app
from forms import add_category as form_add_category

add_category_bp = Blueprint("add_category", __name__)


@add_category_bp.route("/add category", methods=["GET", "POST"])
@fresh_login_required
def add_category():
    if current_user.role == "admin":
        form = form_add_category()
        if form.validate_on_submit():
            if form.sub_category.data != '':

                new_cat = app.Category(category=form.category.data, sub_category=form.sub_category.data)
            else:
                new_cat = app.Category(category=form.category.data)
            app.db.session.add(new_cat)
            app.db.session.commit()
            return redirect(url_for('admin_panel.admin_panel'))

        response = make_response(render_template("add_category.html", form=form))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
