from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,PasswordField,SubmitField, RadioField, BooleanField, SelectMultipleField, widgets, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, InputRequired
from run import Profile

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RegistrationForm(FlaskForm):
    first_name=StringField(validators=[DataRequired(), Length(min=2, max=30)])
    last_name=StringField(validators=[DataRequired(), Length(min=2, max=30)])
    email=StringField(validators=[DataRequired(), Length(min=6,max=30)])
    number=StringField(validators=[DataRequired(), Email()])
    state=StringField(validators=[DataRequired(), Length(min=4,max=100)])
    password=PasswordField(validators=[DataRequired(), Length(min=8,max=20)])  
    confirmPassword=PasswordField(validators=[DataRequired(), EqualTo('password')])
    role= RadioField(choices=[('student','Student'),('teacher','Teacher')], default='student')
    string_of_files = ['Maths\r\nEnglish\r\nPhysics\r\nChemistry\r\nBiology\r\nComputer Science\r\nOthers']
    list_of_files = string_of_files[0].split() 
    # create a list of value/description tuples
    files = [(x, x) for x in list_of_files]
    fields=MultiCheckboxField('Label', choices=files, default=files[-1])
    submit=SubmitField('Signup')

    def validate_email(self, email):
        profile=Profile.query.filter_by(email=email.data).first()
        if profile:
            raise ValidationError('Email has already been taken.')

    def validate_number(self, number):
        profile=Profile.query.filter_by(number=number.data).first()
        if profile:
            raise ValidationError('Phone number has already been taken.')

class UpdateForm(FlaskForm):
    first_name=StringField(validators=[DataRequired(), Length(min=2, max=30)])
    last_name=StringField(validators=[DataRequired(), Length(min=2, max=30)])
    picture=FileField('Update your profile picture', validators=[FileAllowed(['jpg','png'])])
    email=StringField(validators=[DataRequired(), Email()])
    number=StringField(validators=[DataRequired(), Length(min=4,max=20)])
    state=StringField(validators=[DataRequired(), Length(min=4,max=100)])
    submit=SubmitField('Save changes')

    def validate_email(self, email):
        if current_user.profile.email != email.data:
            profile=Profile.query.filter_by(email=email.data).first()
            if profile:
                raise ValidationError('Email has already been taken.')

    def validate_number(self, number):
        if current_user.profile.number != number.data: 
            profile=Profile.query.filter_by(number=number.data).first()
            if profile:
                raise ValidationError('Phone number has already been taken.')
            
class LoginForm(FlaskForm):
    email=StringField(validators=[DataRequired(), Email()])
    password=PasswordField('Password',validators=[DataRequired(), Length(min=4,max=20)])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

class CreatePostForm(FlaskForm):
    picture=FileField('Put your Ad', validators=[DataRequired(), FileAllowed(['jpg','png'])])
    description=TextAreaField(validators=[DataRequired(), Length(min=1, max=120)])
    price=IntegerField('',validators=[DataRequired()])
    string_of_files = ['Maths\r\nEnglish\r\nPhysics\r\nChemistry\r\nBiology\r\nComputer Science\r\nOthers']
    list_of_files = string_of_files[0].split()
    # create a list of value/description tuples
    files = [(x, x) for x in list_of_files]
    fields=MultiCheckboxField('Label', choices=files, default=files[-1])

    
    submit=SubmitField('Post Ad')

class CreateSuggForm(FlaskForm):
    description=TextAreaField(validators=[DataRequired(), Length(min=1, max=120)])
    submit=SubmitField('Suggest')

class PostCommentsForm(FlaskForm):
    description=TextAreaField(validators=[DataRequired(), Length(min=1, max=120)])
    submit=SubmitField('Comment')

class SuggCommentForm(FlaskForm):
    description=TextAreaField(validators=[DataRequired(), Length(min=1, max=120)])
    submit=SubmitField('Comment')

class ResetRequestForm(FlaskForm):
    email=StringField(validators=[DataRequired(), Email()])
    submit=SubmitField('Request Password Reset')

    def validate_email(self, email):
        profile=Profile.query.filter_by(email=email.data).first()
        if not profile:
            raise ValidationError('There is no registered account with that email.')

class ResetPasswordForm(FlaskForm):
    password=PasswordField(validators=[DataRequired(), Length(min=8,max=20)])  
    confirmPassword=PasswordField(validators=[DataRequired(), EqualTo('password')])
    submit=SubmitField('Save Password')