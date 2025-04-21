from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField,EmailField,PasswordField,SubmitField,BooleanField,RadioField
from wtforms.validators import DataRequired,EqualTo,Email

class Register(FlaskForm):
    fname = StringField("First Name", validators=[DataRequired()])
    lname = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Enter password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    user = RadioField("Register as",choices=[("landlord", "Landlord"), ("tenant", "Tenant")],validators=[DataRequired()],)
    terms = BooleanField("Agree to terms and conditions", validators=[DataRequired()])
    register = SubmitField("Register")

class Login(FlaskForm):
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Enter password", validators=[DataRequired()])
    login = SubmitField("Login")

class AdminRegister(FlaskForm):
    username = StringField("Admin Username", validators=[DataRequired()])
    password = PasswordField("Enter password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    register = SubmitField("Register")


class AdminLogin(FlaskForm):
    username = StringField("Admin Username", validators=[DataRequired()])
    password = PasswordField("Enter password", validators=[DataRequired()])
    login = SubmitField("Login")


class DpForm(FlaskForm):
    photo = FileField(
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png", "jpeg", "Only images are allowed"]),
        ]
    )
    uploadbtn = SubmitField("Upload Picture")
