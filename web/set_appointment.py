import calendar
import datetime

import htmlentities
from flask import render_template, request, make_response, Blueprint
from flask_login import current_user, fresh_login_required

import app
import functions

set_appointment_bp = Blueprint("set_appointment", __name__)


@set_appointment_bp.route("/main", methods=["GET", "POST"])
@fresh_login_required
def set_appointment():  # main
    # category_col = Category.query.all()
    user_cat = app.User.query.filter_by(role="lecturer").all()
    catgories = []
    for i in user_cat:
        if "," in i.category:
            for j in i.category.split(","):
                catgories.append(j)
        else:
            catgories.append(i.category)
    catgories = list(set(catgories))  # create list for the categories buttons
    tags = []
    for i in user_cat:
        try:
            if "|" in i.tags:
                for j in i.tags.split("|"):
                    tags.append(j)
            else:
                tags.append(i.tags)
        except:
            continue
    tags = list(set(tags))
    if request.method == "POST" and "record" in request.form:  # if the user want the records of the category he choose
        records = app.Record.query.filter_by(tags=request.form["record"]).all()
        record_cat = request.form["record"]
        records_len = range(len(records))
        response = make_response(
            render_template("main.html", len_tags=range(len(tags)), records_len=records_len, records=records,
                            record_cat=record_cat, cat=catgories, user_cat=user_cat, tags=tags,
                            len_cat=range(len(catgories)), ))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    if request.method == "POST" and "ap_date" in request.form:  # if the user order appointment
        add_user_to_appo = app.Appointment.query.filter_by(uname=request.form["ap_uname"],
                                                           appo_date=request.form["ap_date"],
                                                           appo_start_hour=request.form["ap_hour_st"]).first()
        if add_user_to_appo.appo_user_aproved:
            if add_user_to_appo.appo_user_wait.find(
                    "\n" + current_user.uname + " ") != -1 or add_user_to_appo.appo_user_aproved.find(
                "\n" + current_user.uname + " ") != -1:  # if the user already approved or wait
                response = make_response(
                    render_template("main.html", cat=catgories, user_cat=user_cat, tags=tags, found=""))
                response.headers[
                    'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
                return response

        if add_user_to_appo.appo_user_wait:
            add_user_to_appo.appo_user_wait = add_user_to_appo.appo_user_wait + "\n" + current_user.fname + " " + current_user.lname + " " + current_user.uname + " " + htmlentities.encode(
                request.form["ap_com"])  # if the appo_user_wait already have users
        else:  # if this is the first user
            add_user_to_appo.appo_user_wait = "\n" + current_user.fname + " " + current_user.lname + " " + current_user.uname + " " + \
                                              htmlentities.encode(request.form["ap_com"])  # if this is the first uder
        app.db.session.commit()
        response = make_response(
            render_template("main.html", len_tags=range(len(tags)), cat=catgories, user_cat=user_cat,
                            len_cat=range(len(catgories)), tags=tags, found="", records=""))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response
    elif request.method == "POST":
        d = datetime.datetime.now()
        found = app.User.query.filter_by(uname=request.form["val"]).all()  # get details about the lecterur
        appo_user = app.Appointment.query.filter_by(uname=request.form["val"]).order_by(app.Appointment.appo_date,
                                                                                        app.Appointment.appo_start_hour).all()  # get all appointments
        month_appo = []  # get all appointments available in the current month ⬇️
        for i in appo_user:
            if i.appo_date.split("-")[1] == str(d.month) and i.appo_date.split("-")[0] == str(d.year):
                month_appo.append(i)
            elif i.appo_date.split("-")[1][1] == str(d.month) and i.appo_date.split("-")[0] == str(d.year):
                month_appo.append(i)
        # creating a calendar⬇️
        cal = calendar.HTMLCalendar(firstweekday=6)  # day 6 is sunday
        cal = cal.formatmonth(d.year, d.month)
        # change the days name to hebrew ⬇️
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        h_days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]  # change the days name to hebrew
        for i in range(7):
            cal = cal.replace(days[i], h_days[i], 1)
        # end the day name change
        # split the days for using modal⬇️
        cal = cal.split("<td ")
        tmp_lst = []  # tmp_lst is used for storage the dates and hour_lst_string in this format[day of date,meeting hours] for example ["03","aaaaA","22","bbbb"]
        hour_lst_string = ""  # hour lst string is ther button for call the modal
        for i in range(len(cal)):  # check every table cell in the calender table
            for check_appo in month_appo:
                tmp_date = check_appo.appo_date.split("-")[2]
                if tmp_date in cal[i]:
                    if check_appo.appo_user_aproved:
                        if len(check_appo.appo_user_aproved.split("\n")[
                               1:]) == check_appo.appo_limit:  # if the meeting is full and all users approved
                            hour_lst_string = functions.main_page.red(check_appo)
                        elif len(check_appo.appo_user_aproved.split("\n")[1:]) + len(
                                check_appo.appo_user_wait.split("\n")[
                                1:]) == check_appo.appo_limit:  # if the users wait for approve is full
                            hour_lst_string = functions.main_page.yellow(check_appo)
                        else:
                            hour_lst_string = functions.main_page.green(check_appo)  # if the meeting isnt full
                    elif check_appo.appo_user_wait:  # if the users wait for approve is full
                        if len(check_appo.appo_user_wait.split("\n")) == check_appo.appo_limit + 1:
                            hour_lst_string += functions.main_page.yellow(check_appo)
                        else:  # if the meeting isnt full
                            hour_lst_string = functions.main_page.green(check_appo)
                    else:  # if the meeting isnt full
                        hour_lst_string += functions.main_page.green(check_appo)
                    if tmp_date not in tmp_lst:  # add the date to tmp_lst
                        tmp_lst.append(tmp_date)

                elif tmp_date[1] in cal[i] and check_appo.appo_date.split("-")[2][0] == "0":
                    # in case the date is 1,2,3,4,5,6,7,8,9 becuase the dates save as 01,02,03...⬆
                    if check_appo.appo_user_aproved:
                        if len(check_appo.appo_user_aproved.split("\n")[1:]) == check_appo.appo_limit:
                            hour_lst_string = functions.main_page.red(check_appo)
                        elif len(check_appo.appo_user_aproved.split("\n")[1:]) + len(
                                check_appo.appo_user_wait.split("\n")[1:]) == check_appo.appo_limit:
                            hour_lst_string = functions.main_page.yellow(check_appo)
                        else:
                            hour_lst_string = functions.main_page.green(check_appo)
                    elif check_appo.appo_user_wait:
                        if len(check_appo.appo_user_wait.split("\n")[1:]) == check_appo.appo_limit:
                            hour_lst_string += functions.main_page.yellow(check_appo)
                        else:
                            hour_lst_string = functions.main_page.green(check_appo)
                    else:
                        hour_lst_string += functions.main_page.green(check_appo)
                    if tmp_date not in tmp_lst:  # add the date to tmp_lst
                        tmp_lst.append(tmp_date)
                for j in range(len(tmp_lst)):  # storage all the dates and hour_lst_string

                    if tmp_date == tmp_lst[j]:  # if the date in the list
                        if j + 1 == len(tmp_lst):  # if this is the first appo found create new index
                            tmp_lst.append(hour_lst_string)
                        else:
                            tmp_lst[j + 1] += hour_lst_string  # else add the meeting to eleemnt value
                        hour_lst_string = ""
            for j in range(0, len(tmp_lst), 2):  # add to dropdown menu
                if tmp_lst[j][0] == "0":  # in case the date is 01,02,03,04
                    tmp_lst[j] = tmp_lst[j][1]
                cal[i] = cal[i].replace(">" + tmp_lst[j],
                                        "><div class='dropdown'><button type='button' class='btn btn-primary dropdown-toggle' data-bs-toggle='dropdown'>" +
                                        tmp_lst[j] + "</button>\n<ul class='dropdown-menu'>" + tmp_lst[
                                            j + 1] + "</ul></div>")  # create dropdown menu with the hours for every day meeting is available
                hour_lst_string = ""
        cal = "<td ".join(cal)
        response = make_response(
            render_template("main.html", len_tags=range(len(tags)), cat=catgories, user_cat=user_cat, tags=tags,
                            len_cat=range(len(catgories)), found=found,
                            caln=cal.replace('<td ', '<td  width="150" height="150"'),
                            month_appo=month_appo))
        response.headers[
            'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
        return response

    response = make_response(
        render_template("main.html", len_tags=range(len(tags)), cat=catgories, user_cat=user_cat, tags=tags,
                        len_cat=range(len(catgories)), found="", records=""))
    response.headers[
        'Content-Security-Policy'] = app.defualt_content_policy + ";" + app.js_content_policy + ";" + app.css_content_policy + ";"
    return response
