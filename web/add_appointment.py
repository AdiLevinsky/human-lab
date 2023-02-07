import datetime

import htmlentities
from flask import render_template, redirect, url_for, flash, abort, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app
from forms import add_Appointment

add_appointment_bp = Blueprint("add_appointment", __name__)


@add_appointment_bp.route("/add appointment", methods=["GET", "POST"])
@fresh_login_required
def add_appointment():
    if current_user.role == "admin" or current_user.role == "lecturer":
        form = add_Appointment()
        if form.validate_on_submit():
            # get the date from the form⬇️
            num_date = form.appo_date.data.strftime("%Y-%m-%d")
            # get the hour from the form⬇️
            start_hour = form.appo_hour.data.strftime("%H:%M")
            # create new datatime object
            full_date = datetime.datetime(form.appo_date.data.year,
                                          form.appo_date.data.month,
                                          form.appo_date.data.day,
                                          form.appo_hour.data.hour,
                                          form.appo_hour.data.minute)
            # caluclate the time the meeting will end
            end_appo = (full_date + datetime.timedelta(minutes=int(form.appo_dur.data))).time().strftime("%H:%M")
            # check if another appoinmtment is already exist in this time⬇️
            appo_set = app.Appointment.query.filter_by(uname=current_user.uname, appo_date=num_date).all()
            for ap_set in appo_set:
                if ap_set.appo_start_hour <= start_hour <= ap_set.appo_end_hour \
                        or ap_set.appo_start_hour <= end_appo <= ap_set.appo_end_hour \
                        or ap_set.appo_start_hour >= start_hour and ap_set.appo_end_hour <= end_appo:
                    flash("הזמן כבר תפוס")
                    return redirect(url_for("add_appointment.add_appointment"))
            # add appointmnet the datebase ⬇️
            new_appo = app.Appointment(uname=current_user.uname,
                                       fname=current_user.fname,
                                       lname=current_user.lname,
                                       appo_date=num_date,
                                       appo_start_hour=start_hour,
                                       appo_end_hour=end_appo,
                                       appo_loc=htmlentities.encode(form.appo_loc.data),
                                       appo_type=htmlentities.encode(form.appo_type.data),
                                       appo_limit=form.appo_limit.data,
                                       appo_dur=form.appo_dur.data)
            app.db.session.add(new_appo)
            app.db.session.commit()
            return redirect(url_for("lecturer_panel.lecturer_panel"))

        response = make_response(render_template("add_appointment.html", form=form))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
