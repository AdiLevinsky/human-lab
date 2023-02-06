import datetime

from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app

edit_appointment_bp = Blueprint("edit_appointment", __name__)


@edit_appointment_bp.route("/edit appointment", methods=["POST"])
@fresh_login_required
def edit_appointment():
    if current_user.role == "admin" or current_user.role == "lecturer":
        # update appointment details⬇️
        if "ap_date1" in request.form:
            # num_date = request.form["ap_date1"].strftime("%Y-%m-%d")
            splited_date = request.form["ap_date1"].split("-")
            if len(splited_date) != 3:
                return abort(403)

            start_hour = request.form["ap_hour_st1"]
            start_hour_split = request.form["ap_hour_st1"].split(":")
            if len(start_hour_split) != 2:
                return abort(403)
            try:

                full_date = datetime.datetime(int(splited_date[0]),
                                              int(splited_date[1]),
                                              int(splited_date[2]),
                                              int(start_hour_split[0]),
                                              int(start_hour_split[1]))
            except:
                return abort(403)

            end_appo = (full_date + datetime.timedelta(minutes=int(request.form["ap_dur1"]))).time().strftime("%H:%M")
            appo_set = app.Appointment.query.filter_by(uname=request.form["lect"],
                                                       appo_date=request.form["ap_date1"]).all()
            for ap_set in appo_set:
                if (ap_set.appo_start_hour <= start_hour <= ap_set.appo_end_hour) \
                        or (ap_set.appo_start_hour <= end_appo <= ap_set.appo_end_hour) \
                        or (ap_set.appo_start_hour >= start_hour and ap_set.appo_end_hour <= end_appo):
                    if ap_set.id != int(request.form["id"]):
                        response = make_response(render_template("edit_appo.html",
                                                                 ap_date=request.form["ap_date1"],
                                                                 ap_hour_st=request.form["ap_hour_st1"],
                                                                 ap_dur=request.form["ap_dur1"],
                                                                 ap_loc=request.form["ap_loc1"],
                                                                 ap_limit=request.form["appo_limit1"],
                                                                 ap_type=request.form["appo_type1"],
                                                                 ap_id=request.form["id"],
                                                                 ty=["פרטני", "קבוצה"], error="הזמן כבר תפוס",
                                                                 current_user=current_user))
                        response.headers[
                            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                        return response

            up_appo = app.Appointment.query.filter_by(id=request.form["id"]).first()
            if up_appo.appo_date != request.form[
                "ap_date1"] or up_appo.uname != current_user.uname and current_user.id != 1:
                return abort(403)
            up_appo.appo_date = request.form["ap_date1"]
            up_appo.appo_start_hour = request.form["ap_hour_st1"]
            up_appo.appo_dur = request.form["ap_dur1"]
            up_appo.appo_loc = request.form["ap_loc1"]
            up_appo.appo_end_hour = end_appo
            up_appo.appo_limit = request.form["appo_limit1"]
            up_appo.appo_type = request.form["appo_type1"]
            app.db.session.commit()
            if current_user.id == 1:
                return redirect(url_for("admin_panel.admin_panel"))

            return redirect(url_for("lecturer_panel.lecturer_panel"))
        elif "ap_date" in request.form:
            if request.form["action2"] == "ערוך פגישה זאת":  # go to update details webpage
                if "lect_name" in request.form and current_user.id == 1:

                    up_appo = app.Appointment.query.filter_by(uname=request.form["lect_name"],
                                                              appo_date=request.form["ap_date"],
                                                              appo_start_hour=request.form["ap_hour_st"]).first()
                else:
                    up_appo = app.Appointment.query.filter_by(uname=current_user.uname,
                                                              appo_date=request.form["ap_date"],
                                                              appo_start_hour=request.form["ap_hour_st"]).first()
                response = make_response(render_template("edit_appo.html",
                                                         lect=up_appo.uname,
                                                         ap_id=up_appo.id,
                                                         ap_date=request.form["ap_date"],
                                                         ap_hour_st=request.form["ap_hour_st"],
                                                         ap_dur=request.form["ap_dur"],
                                                         ap_loc=request.form["ap_loc"],
                                                         ap_limit=request.form["ap_limit"],
                                                         ap_type=request.form["ap_type"],
                                                         ty=["פרטני", "קבוצה"], current_user=current_user))
                response.headers[
                    'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                return response

            elif request.form["action2"] == "שלח הודעה":  # send message for all students
                if "lect_name" in request.form and current_user.id == 1:

                    up_appo = app.Appointment.query.filter_by(uname=request.form["lect_name"],
                                                              appo_date=request.form["ap_date"],
                                                              appo_start_hour=request.form["ap_hour_st"]).first()
                else:
                    up_appo = app.Appointment.query.filter_by(uname=current_user.uname,
                                                              appo_date=request.form["ap_date"],
                                                              appo_start_hour=request.form["ap_hour_st"]).first()
                response = make_response(render_template("send_msg.html",
                                                         lect=up_appo.uname,
                                                         ap_id=up_appo.id,
                                                         ap_date=request.form["ap_date"],
                                                         ap_hour_st=request.form["ap_hour_st"],
                                                         ap_loc=request.form["ap_loc"], appo_msg=request.form["msgs"],
                                                         current_user=current_user))
                response.headers[
                    'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + " http://127.0.0.1:5000/static/css/send_msg.css "
                return response
            elif request.form["action2"] == "מחק":  # delete appointment
                if "lect_name" in request.form and current_user.id == 1:

                    app.Appointment.query.filter_by(uname=request.form["lect_name"],
                                                    appo_date=request.form["ap_date"],
                                                    appo_start_hour=request.form["ap_hour_st"]).delete()
                    app.db.session.commit()
                    return redirect(url_for("admin_panel.admin_panel"))
                else:
                    app.Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                    appo_start_hour=request.form["ap_hour_st"]).delete()
                    app.db.session.commit()
                    return redirect(url_for("lecturer_panel.lecturer_panel"))
    else:
        return abort(403)
