from flask import redirect, url_for, abort, request, Blueprint
from flask_login import current_user, fresh_login_required

import app

send_msg_bp = Blueprint("send_msg", __name__)


@send_msg_bp.route("/send msg", methods=["POST"])
@fresh_login_required
def send_msg():
    if current_user.role == "lecturer" or current_user.role == "admin":
        curr_appo = app.Appointment.query.filter_by(uname=request.form["lect"],
                                                    appo_date=request.form["ap_date1"],
                                                    appo_start_hour=request.form[
                                                        "ap_hour_st1"]).first()  # get appointment by lecturer date and hour
        curr_appo.appo_msg = request.form["text"]  # create new message
        app.db.session.commit()
        if current_user.id == 1:
            return redirect(url_for('admin_panel.admin_panel'))
        return redirect(url_for("lecturer_panel.lecturer_panel"))
    else:
        return abort(403)
