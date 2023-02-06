from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app

lecturer_panel_bp = Blueprint("lecturer_panel", __name__)


@lecturer_panel_bp.route("/lect panel", methods=["GET", "POST"])
@fresh_login_required
def lecturer_panel():
    if current_user.role == "admin" or current_user.role == "lecturer":
        if request.method == "POST":
            if request.form[
                "action"] == "אישור":  # delete the users from the waiting to approve column in the row of the appoinntment and add the user the approved users for the appointment
                appo_approve = app.Appointment.query.filter_by(uname=current_user.uname,
                                                               appo_date=request.form["ap_date"],
                                                               appo_start_hour=request.form["ap_hour_st"]).first()
                if appo_approve.appo_user_aproved:
                    appo_approve.appo_user_aproved = appo_approve.appo_user_aproved + "\n" + request.form["add_user"]
                    appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace("\n" + request.form["add_user"],
                                                                                      "")

                else:
                    appo_approve.appo_user_aproved = "\n" + request.form["add_user"]
                    appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace("\n" + request.form["add_user"],
                                                                                      "")
                app.db.session.commit()
                return redirect(url_for("lecturer_panel.lecturer_panel"))
            elif request.form[
                "action"] == "דחייה":  # delete the users from the waiting to approve column in the row of the
                # appoinntment
                appo_rej = app.Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                           appo_start_hour=request.form["ap_hour_st"]).first()
                appo_rej.appo_user_wait = appo_rej.appo_user_wait.replace("\n" + request.form["add_user"], "")
                app.db.session.commit()
                redirect(url_for("lecturer_panel.lecturer_panel"))
            elif request.form["action"] == "מחק":  # delete the users from the approved users for the appointment
                appo_del = app.Appointment.query.filter_by(uname=current_user.uname, appo_date=request.form["ap_date"],
                                                           appo_start_hour=request.form["ap_hour_st"]).first()
                appo_del.appo_user_aproved = appo_del.appo_user_aproved.replace("\n" + request.form["del_user"], "")
                if not appo_del.appo_user_aproved:
                    appo_del.appo_user_aproved == ""
                app.db.session.commit()
                return redirect(url_for("lecturer_panel.lecturer_panel"))

        appo_user = app.Appointment.query.filter_by(uname=current_user.uname).order_by(app.Appointment.appo_date,
                                                                                       app.Appointment.appo_start_hour).all()  # get all user appointments
        table_len = range(len(appo_user))
        for i in table_len:
            if appo_user[i].appo_user_wait:  # if its not none
                temp = appo_user[i].appo_user_wait.replace("\n", "")
                if temp:
                    appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.split("\n")[
                                                  1:]  # the users in appo_user_wait save \n name...\n name \n ..... so get list of all users i split by \n
                    appo_user[i].appo_user_wait.append(len(appo_user[
                                                               i].appo_user_wait))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                else:
                    appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.replace("\n",
                                                                                      "")  # else if no user wait for approve the objects value become to "" which is nothing
            if appo_user[i].appo_user_aproved:  # if its not none
                temp = appo_user[i].appo_user_aproved.replace("\n", "")
                if temp:
                    appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.split("\n")[
                                                     1:]  # the users in appo_user_aproved save \n name...\n name \n ..... so get list of all users i split by \n
                    appo_user[i].appo_user_aproved.append(len(appo_user[
                                                                  i].appo_user_aproved))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                else:
                    appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.replace("\n",
                                                                                            "")  # else if no user wait for approve the objects value become to "" which is nothing
        response = make_response(
            render_template("lecturer_panel.html", table_len=table_len, appo_user=appo_user, current_user=current_user))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    else:
        return abort(403)
