from flask import render_template, redirect, url_for, abort, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app
from forms import add_record as add_record_form

add_record_bp = Blueprint("add_record", __name__)


@add_record_bp.route("/add record", methods=["POST", "GET"])
@fresh_login_required
def add_record():
    if current_user.role == "admin":
        # classic add item in this case record(record category,tags,record title,record link,record description)
        cat = app.Category.query.all()  # fetch all categories from category table
        form = add_record_form()
        form.record_category.choices = [(i.category, i.category) for i in cat]
        sub_categories = []
        for i in cat:
            col_sub_category = str(i.sub_category).split("_")
            for j in col_sub_category:
                tmp = (i.category + '_' + j, j)
                sub_categories.append(tmp)

        form.tags.choices = sub_categories
        if form.validate_on_submit():
            new_record = app.Record(category=",".join(form.record_category.data),
                                    tags="|".join(form.tags.data),
                                    title=form.record_title.data,
                                    link=form.record_link.data,
                                    desc=form.record_desc.data)
            app.db.session.add(new_record)
            app.db.session.commit()
            return redirect(url_for('admin_panel.admin_panel'))

        response = make_response(render_template("add_record.html", form=form))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
