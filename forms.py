from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, SelectMultipleField, FileField, DateField, TimeField, \
    SelectField, IntegerField, widgets
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    uname = StringField("שם משתמש", validators=[DataRequired()])
    password = PasswordField("סיסמה", validators=[DataRequired()])
    submit = SubmitField("כניסה")

class add_student(FlaskForm):
    uname = StringField("שם משתמש", validators=[DataRequired()])
    fname = StringField("שם פרטי", validators=[DataRequired()])
    lname = StringField("שם משפחה", validators=[DataRequired()])
    password = PasswordField("סיסמה", validators=[DataRequired()])
    submit = SubmitField("הוסף")

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class add_Lecturer(FlaskForm):
    uname = StringField("שם משתמש", validators=[DataRequired()])
    fname = StringField("שם פרטי", validators=[DataRequired()])
    lname = StringField("שם משפחה", validators=[DataRequired()])
    password = PasswordField("סיסמה", validators=[DataRequired()])
    #category = SelectMultipleField('בחר קטגוריה',validators=[DataRequired()],widget = widgets.CheckboxInput())
    category = MultiCheckboxField('בחר קטגוריה')
    tags = MultiCheckboxField('בחר תת קטגוריה')
    desc = StringField("תיאור",validators=[DataRequired()])
    image = FileField(validators=[FileAllowed(["jpg","png"],"רק תמונות")])
    submit = SubmitField("הוסף")

class add_Appointment(FlaskForm):
    appo_date = DateField("תאריך הפגישה",validators=[DataRequired()],render_kw=({"min":datetime.now().strftime("%Y-%m-%d")}))
    appo_hour = TimeField("שעת הפגישה",validators=[DataRequired(),],render_kw=({"min":"08:30","max":"23:59"}))
    appo_dur = IntegerField("משך הפגישה בדקות",validators=[DataRequired()],render_kw=({"min":"1"}))
    appo_loc = StringField("מיקום הפגישה",validators=[DataRequired()])
    appo_type = SelectField("סוג הפגישה",choices=[('פרטני','פרטני'),('קבוצה','קבוצה')],validators=[DataRequired()],render_kw=({"min":"1"}))
    appo_limit = IntegerField("כמות אנשים",validators=[DataRequired()],default=1)
    submit = SubmitField("הוסף")

class add_record(FlaskForm):
    record_category = MultiCheckboxField('בחר קטגוריה')
    tags = MultiCheckboxField('בחר תת קטגוריה')
    record_title = StringField("כותרת",validators=[DataRequired()])
    record_desc = StringField("תיאור", validators=[DataRequired()])
    record_link = StringField("לינק", validators=[DataRequired()])
    submit = SubmitField("הוסף")

class add_category(FlaskForm):
    category = StringField("קטגוריה", validators=[DataRequired()])
    sub_category = StringField("תת קטגוריות (להפריד בין התת קטוגוריות עם _ )")
    submit = SubmitField("הוסף")
