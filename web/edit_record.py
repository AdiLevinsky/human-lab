from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app

edit_record_bp = Blueprint("edit_record", __name__)


@edit_record_bp.route("/edit record", methods=["POST"])
@fresh_login_required
def edit_record():
    if current_user.id == 1:
        if request.method == "POST":
            if "action2" in request.form:  # update the record
                app.Record.query.filter_by(link=request.form["rec_link"]).delete()
                app.db.session.commit()
                return redirect(url_for("admin_panel.admin_panel"))
            elif "title1" in request.form:  # title1 is only exist in the update form
                rec = app.Record.query.filter_by(id=request.form["id1"]).first()
                records = app.Record.query.all()
                category_col = app.Category.query.all()
                rec.category = ",".join([i.category for i in category_col if i.category in request.form])
                tags = []
                for i in category_col:
                    for j in i.sub_category.split("_"):
                        if i.category + "_" + j in request.form:
                            tags.append(i.category + "_" + j)
                rec.tags = "|".join(tags)

                category = [i.category for i in category_col]
                checked_category = [i.category for i in category_col if i.category in request.form]
                # for i in request.form["category"].split(","):
                #     if i in category:
                #         checked_category.append(i)
                sub_categories = []
                for i in category_col:
                    sub_category_col = str(i.sub_category).split("_")
                    for j in sub_category_col:
                        tmp = i.category + '_' + j
                        sub_categories.append(tmp)
                for i in records:
                    if i.link == request.form["link1"] and i.id != int(request.form["id1"]):
                        response = make_response(render_template("edit_record.html", category=category,
                                                                 category_len=range(len(category)),
                                                                 checked_category=checked_category,
                                                                 tags=sub_categories,
                                                                 tags_len=range(len(sub_categories)),
                                                                 link=request.form["link1"],
                                                                 desc=request.form["desc1"],
                                                                 title=request.form["title1"],
                                                                 rec_id1=request.form["id1"],
                                                                 error="הקלטה זאת נמצאת כבר"))
                        response.headers[
                            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                        return response

                rec.link = request.form["link1"]
                rec.desc = request.form["desc1"]
                rec.title = request.form["title1"]
                app.db.session.commit()
                return redirect(url_for("admin_panel.admin_panel"))
            elif "rec_title" in request.form:  # rec_title only exist in froms inside the table in admin panel,redirect to edit record
                category_col = app.Category.query.all()  # fetch all categories

                category = [i.category for i in category_col]
                checked_category = request.form["rec_category"].split(",")
                # for i in request.form["category"].split(","):
                #     if i in category:
                #         checked_category.append(i)
                sub_categories = []
                for i in category_col:
                    sub_category_col = str(i.sub_category).split("_")
                    for j in sub_category_col:
                        tmp = i.category + '_' + j
                        sub_categories.append(tmp)
                rec_id = app.Record.query.filter_by(link=request.form["rec_link"]).first().id
                response = make_response(render_template("edit_record.html", category=category,
                                                         category_len=range(len(category)),
                                                         checked_category=checked_category,
                                                         tags=sub_categories,
                                                         tags_len=range(len(sub_categories)),
                                                         checked_tags=request.form["rec_tags"].split("|"),
                                                         link=request.form["rec_link"],
                                                         desc=request.form["rec_desc"],
                                                         title=request.form["rec_title"],
                                                         rec_id1=rec_id))
                response.headers[
                    'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                return response
    else:
        return abort(403)
