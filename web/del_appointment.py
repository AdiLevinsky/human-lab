from flask import redirect, url_for, abort, request, Blueprint
from flask_login import current_user, fresh_login_required

import app

del_appointment_bp = Blueprint("del_appointment", __name__)


@del_appointment_bp.route("/del appointment", methods=["POST"])
@fresh_login_required
def del_appointment():
    if current_user.role == "student":
        if request.method == "POST":
            appo_del = app.Appointment.query.filter_by(uname=request.form["lect_name"],
                                                       appo_date=request.form["ap_date"],
                                                       appo_start_hour=request.form[
                                                           "ap_hour_st"]).first()  # get appointment
            appo_del.appo_user_aproved = appo_del.appo_user_aproved.replace(
                "\n" + current_user.fname + " " + current_user.lname + " " + current_user.uname, "")  # delete the user
            if not appo_del.appo_user_aproved:
                appo_del.appo_user_aproved == ""
            app.db.session.commit()
        return redirect(url_for('student_profile.student_profile'))
    else:
        return abort(403)
