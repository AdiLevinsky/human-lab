import htmlentities
from flask import render_template, redirect, url_for, abort, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app

admin_panel_bp = Blueprint("admin_panel", __name__)


@admin_panel_bp.route('/adminPanel', methods=["GET", "POST"])
@fresh_login_required
def admin_panel():
    if current_user.id == 1:
        if request.method == "POST":
            # show the table choosen by the admin
            try:
                choose = htmlentities.encode(request.form["choose"])
            except:
                choose = ""
            if choose == "users":
                student_tb = app.User.query.filter_by(role="student").all()  # get all students
                table_len = range(len(student_tb))  # table len is for the for loop in the html
                response = make_response(render_template("adminPanel.html", table_len=table_len, st_table=student_tb,
                                                         current_user=current_user, choose=choose))
                response.headers['Content-Security-Policy'] = app.defualt_content_policy + \
                                                              ";" + app.js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + \
                                                              app.css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
            elif choose == "lecturers":
                student_tb = app.User.query.filter_by(role="lecturer").all()  # get all lecterurs
                table_len = range(len(student_tb))  # table len is for the for loop in the html
                response = make_response(render_template("adminPanel.html", table_len=table_len, st_table=student_tb,
                                                         current_user=current_user, choose=choose))
                response.headers['Content-Security-Policy'] = app.defualt_content_policy + \
                                                              ";" + app.js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + \
                                                              app.css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response

            elif choose == "appos":
                if "search1" in request.form:
                    appo_user = app.Appointment.query.filter_by(uname=request.form["search1"]).order_by(
                        app.Appointment.appo_date,
                        app.Appointment.appo_start_hour).all()
                else:
                    appo_user = app.Appointment.query.order_by(app.Appointment.appo_date,
                                                               app.Appointment.appo_start_hour).all()  # get all users appointments

                table_len = range(len(appo_user))  # table len is the length of the table
                for i in table_len:
                    if appo_user[i].appo_user_wait:  # if it's not none
                        temp = appo_user[i].appo_user_wait.replace("\n", "")
                        if temp:
                            appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.split("\n")[
                                                          1:]  # the users in appo_user_wait save \n name...\n name \n ..... so get list of all users I split by \n
                            appo_user[i].appo_user_wait.append(len(appo_user[
                                                                       i].appo_user_wait))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                        else:
                            appo_user[i].appo_user_wait = appo_user[i].appo_user_wait.replace("\n",
                                                                                              "")  # else if no user wait for approve the objects value become to "" which is nothing
                    if appo_user[i].appo_user_aproved:  # if it's not none
                        temp = appo_user[i].appo_user_aproved.replace("\n", "")
                        if temp:
                            appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.split("\n")[
                                                             1:]  # the users in appo_user_aproved save \n name...\n name \n ..... so get list of all users I split by \n
                            appo_user[i].appo_user_aproved.append(len(appo_user[
                                                                          i].appo_user_aproved))  # add the length of the list in the last elemnt of list to the blocks of delete in the table
                        else:
                            appo_user[i].appo_user_aproved = appo_user[i].appo_user_aproved.replace("\n",
                                                                                                    "")  # else if no user wait for approve the objects value become to "" which is nothing
                response = make_response(
                    render_template("adminPanel.html", table_len=table_len, appo_user=appo_user, choose="appos"))
                response.headers['Content-Security-Policy'] = app.defualt_content_policy + \
                                                              ";" + \
                                                              app.js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + \
                                                              app.css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
            elif choose == "records":
                records_tb = app.Record.query.all()  # get all records
                table_len = range(len(records_tb))  # the length of records table
                response = make_response(
                    render_template("adminPanel.html", table_len=table_len, records_tb=records_tb, choose="records"))
                response.headers['Content-Security-Policy'] = app.defualt_content_policy + \
                                                              ";" + app.js_content_policy + \
                                                              "http://127.0.0.1:5000/static/Javascript/adminpanel.js ; " + \
                                                              app.css_content_policy + \
                                                              "http://127.0.0.1:5000/static/css/adminpanel.css"
                return response
            if "action" in request.form:  # the action name is for confirmation delete and reject
                if request.form[
                    "action"] == "אישור":  # delete the users from the waiting to approve column in the row of the appoinntment and add the user the approved users for the appointment
                    appo_approve = app.Appointment.query.filter_by(uname=htmlentities.encode(request.form["lect_name"]),
                                                                   appo_date=htmlentities.encode(
                                                                       request.form["ap_date"]),
                                                                   appo_start_hour=htmlentities.encode(
                                                                       request.form["ap_hour_st"])).first()
                    if appo_approve.appo_user_aproved:
                        appo_approve.appo_user_aproved = appo_approve.appo_user_aproved + "\n" + htmlentities.encode(
                            request.form["add_user"])  # prevent xss
                        appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace(
                            "\n" + htmlentities.encode(request.form["add_user"]), "")

                    else:
                        appo_approve.appo_user_aproved = "\n" + htmlentities.encode(
                            request.form["add_user"])  # prevent xss
                        appo_approve.appo_user_wait = appo_approve.appo_user_wait.replace(
                            "\n" + htmlentities.encode(request.form["add_user"]), "")  # prevent xss
                    app.db.session.commit()
                    return redirect(url_for("admin_panel.admin_panel"))
                elif request.form[
                    "action"] == "דחייה":  # delete the users from the waiting to approve column in the row of the appoinntment
                    appo_rej = app.Appointment.query.filter_by(uname=htmlentities.encode(request.form["lect_name"]),
                                                               appo_date=htmlentities.encode(request.form["ap_date"]),
                                                               appo_start_hour=htmlentities.encode(
                                                                   request.form["ap_hour_st"])).first()  # prevent xss
                    appo_rej.appo_user_wait = appo_rej.appo_user_wait.replace("\n" + request.form["add_user"],
                                                                              "")  # prevent xss
                    app.db.session.commit()
                    return redirect(url_for("admin_panel.admin_panel"))
                elif request.form["action"] == "מחק":  # delete the users from the approved users for the appointment
                    appo_del = app.Appointment.query.filter_by(uname=request.form["lect_name"],
                                                               appo_date=request.form["ap_date"],
                                                               appo_start_hour=request.form["ap_hour_st"]).first()
                    appo_del.appo_user_aproved = appo_del.appo_user_aproved.replace("\n" + request.form["del_user"], "")
                    if not appo_del.appo_user_aproved:
                        appo_del.appo_user_aproved == ""
                    app.db.session.commit()
                    return redirect(url_for("admin_panel.admin_panel"))
        if request.method == "GET":
            response = make_response(render_template("adminPanel.html", choose="bb"))  # used for check
            response.headers[
                'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + "http://127.0.0.1:5000/static/Javascript/adminpanel.js ;" + app.css_content_policy + "http://127.0.0.1:5000/static/css/adminpanel.css"
            return response

    return abort(403)
