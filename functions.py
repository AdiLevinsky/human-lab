
class main_page():
    def green(check_appo):
        return "<li><button class='dropdown-item btn' style='background-color:green' data-bs-toggle='modal' data-bs-target='#a" + check_appo.appo_date + "-" + "_".join(
                            check_appo.appo_start_hour.split(":")) + "'>" + str(
                            check_appo.appo_start_hour) + "</button></li>"  # making a button call to the  modal and
                        # there is a place in the meeting
    def yellow(check_appo):
        return "<li><button class='dropdown-item btn' disabled style='background-color:#ff8000' data-bs-toggle='modal' data-bs-target='#a" + check_appo.appo_date + "-" + "_".join(
                                check_appo.appo_start_hour.split(":")) + "'>" + str(
                                check_appo.appo_start_hour) + "</button></li>"  # making a button call to the modal and no place left to the appointment but not all users approved
    def red(check_appo):
        return "<li><button class='dropdown-item btn' style='background-color:red' " \
        "disabled data-bs-toggle='modal' data-bs-target='#a" + \
        check_appo.appo_date + "-" + "_".join(
            check_appo.appo_start_hour.split(":")) + "'>" + str(
            check_appo.appo_start_hour) + "</button></li>"  # making a button call to the  modal and no place left to the appointment and all users approved